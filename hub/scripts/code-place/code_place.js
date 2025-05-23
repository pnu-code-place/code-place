// Set to true to enable console log
const debug = false;

// Interval for checking submission state after clicking the submit button (ms)
const POLL_INTERVAL = 500; // 500ms
// Max wait time for submit button to be attached on the DOM (ms)
const SUBMIT_BTN_MAX_WAIT_TIME = 10000; // 10s
// Max wait time for getting ACCEPTED status after submission
const SUBMIT_ACCEPTED_WAIT_TIME = 10000; // 10s

// Interval ID for status checking
let loader = null;
let timer = null;

/**
 * Starts the submission state checking loader
 * Periodically checks submission status and initiates upload when problem is accepted
 * @returns {void}
 */
const startLoader = () => {
  if (loader) {
    log("Loader is already running. Ignoring additional loader.");
    return;
  }

  timer = setTimeout(() => {
    log(
      `Waited Accepted status for ${SUBMIT_ACCEPTED_WAIT_TIME}ms. Stopping loader.`
    );
    stopLoader();
  }, SUBMIT_ACCEPTED_WAIT_TIME);

  loader = setInterval(async () => {
    log("Checking Submission Status...");

    if (!isProblemPage()) {
      log("Out of problem page.");
      stopLoader();
      return;
    }

    const enabled = await checkEnable();
    if (!enabled) {
      stopLoader();
      return;
    }

    const submissionStateElem = document.querySelector(".submissionState");
    if (submissionStateElem === null) return;

    const submissionState = submissionStateElem.textContent.trim();

    if (submissionState === RESULT_CATEGORY.RESULT_ACCEPTED) {
      stopLoader();
      log("Accepted problem detected, Starting upload...");
      showToast(chrome.i18n.getMessage("toast_processing_upload"));
      const coplData = await parseData();
      await beginUpload(coplData);
    }
  }, POLL_INTERVAL);
};

/**
 * Clears the interval and timeout for checking submission status
 * @returns {void}
 */
const stopLoader = () => {
  log("Stopping Loader...");

  if (loader) {
    clearInterval(loader);
    loader = null;
  }

  if (timer) {
    clearTimeout(timer);
    timer = null;
  }
};

/**
 * Updates the extension version
 * @async
 * @returns {Promise<void>}
 */
const versionUpdate = async () => {
  log("Start Version Update");
  const stats = await updateLocalStorageStats();
  // Update Version
  stats.version = getVersion();
  await saveStats(stats);
  log("stats updated.", stats);
};

/**
 * Initiates the upload of problem solution data
 * @async
 * @param {Object} coplData
 * @returns {Promise<void>}
 */
const beginUpload = async (coplData) => {
  if (!isNotEmpty(coplData)) {
    log("coplData is empty. Stop Uploading.");
    return;
  }

  log(`Begin Upload with ${coplData}`);

  const stats = await getStats();
  const hook = await getHook();

  const currentVersion = stats.version;
  if (
    isNull(currentVersion) ||
    currentVersion !== getVersion() ||
    isNull(await getStatsSHAfromPath(hook))
  ) {
    await versionUpdate();
  }

  const cachedSHA = await getStatsSHAfromPath(
    `${hook}/${coplData.directory}/${coplData.sourceCodeFileName}`
  );
  const calcSHA = calculateBlobSHA(coplData.code);
  log("cachedSHA: ", cachedSHA, "calcSHA:", calcSHA);
  if (cachedSHA === calcSHA) {
    log("This source code is already uploaded. Skipping upload.");
    showToast(chrome.i18n.getMessage("toast_duplicate_upload"));
    return;
  }

  await uploadOneSolveProblemOnGit(coplData, () => {
    log("Uploaded complete!");
    showToast(chrome.i18n.getMessage("toast_successful_upload"));
  });
};

/**
 * Sets up a mutation observer to watch for the submission button to appear in the DOM.
 * Once the button is detected, attaches a click event listener that triggers the startLoader function.
 * The observer automatically disconnects either when the button is found or after a maximum wait time.
 * @returns {void}
 */
const setupSubmitListener = () => {
  const startTime = Date.now();

  const observer = new MutationObserver((mutations) => {
    if (Date.now() - startTime > SUBMIT_BTN_MAX_WAIT_TIME) {
      observer.disconnect();
      log("Failed to find Submit Button.");
      return;
    }

    const submitBtn = document.querySelector(".submissionBtnWrapper");
    if (submitBtn) {
      observer.disconnect();
      submitBtn.addEventListener("click", startLoader);
    }
  });
  observer.observe(document.body, {
    childList: true,
    subtree: true,
  });
};

/**
 * Checks if the current page is a problem page
 * @returns {boolean} - True if current page is a problem paage, false otherwise
 */
const isProblemPage = () => {
  const currentUrl = window.location.href;
  return PROBLEM_URL_REGEX.test(currentUrl);
};

/**
 * Background worker sends message if current URL is Problem Detail Page
 * On Problem Detail Page, add callback function on submit button's onclick event
 */
chrome.runtime.onMessage.addListener(async (message, sender, sendResponse) => {
  if (message && message.action === "url_changed_to_problem_detail_page") {
    // Check if local storage is set properly
    const isLocalStorageValid = await checkLocalStorage();
    if (!isLocalStorageValid) {
      showToast(
        chrome.i18n.getMessage("toast_incomplete_setup"),
        "error",
        3000
      );
      return;
    }

    // check Code Place Hub is enabled
    const enabled = await checkEnable();
    if (!enabled) {
      showToast(chrome.i18n.getMessage("toast_disabled"), "info", 3000);
      return;
    }

    showToast(chrome.i18n.getMessage("toast_ready_upload"));
    setupSubmitListener();
  }
});
