  // 브라우저 풀링 방식 -> 디비 조회 방식으로 변경
// Set to true to enable console log
const debug = false;

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
 * Checks if the current page is a problem page
 * @returns {boolean} - True if current page is a problem page, false otherwise
 */
const isProblemPage = () => {
  const currentUrl = window.location.href;
  return PROBLEM_URL_REGEX.test(currentUrl);
};

/**
 * Listen for submission accepted events dispatched by the Code Place web application
 */
window.addEventListener("message", async (event) => {
  if (event.source !== window) return;
  if (event.data && event.data.type === "CODEPLACE_HUB_SUBMISSION_ACCEPTED") {
    log("Accepted problem detected via window message event:", event.data.data);

    if (!isProblemPage()) {
      log("Not a problem page. Ignoring submission event.");
      return;
    }

    const isLocalStorageValid = await checkLocalStorage();
    if (!isLocalStorageValid) {
      showToast(
        chrome.i18n.getMessage("toast_incomplete_setup"),
        "error",
        3000
      );
      return;
    }

    const enabled = await checkEnable();
    if (!enabled) {
      log("Code Place Hub is disabled.");
      return;
    }

    showToast(chrome.i18n.getMessage("toast_processing_upload"));
    const coplData = await makeData(event.data.data);
    await beginUpload(coplData);
  }
});

/**
 * Background worker sends message if current URL is Problem Detail Page
 * Notify user that Code Place Hub is ready
 */
chrome.runtime.onMessage.addListener(async (message, sender, sendResponse) => {
  if (message && message.action === "url_changed_to_problem_detail_page") {
    const isLocalStorageValid = await checkLocalStorage();
    if (!isLocalStorageValid) {
      showToast(
        chrome.i18n.getMessage("toast_incomplete_setup"),
        "error",
        3000
      );
      return;
    }

    const enabled = await checkEnable();
    if (!enabled) {
      showToast(chrome.i18n.getMessage("toast_disabled"), "info", 3000);
      return;
    }

    showToast(chrome.i18n.getMessage("toast_ready_upload"));
  }
});
