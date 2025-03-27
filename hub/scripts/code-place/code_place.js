// Set to true to enable console log
const debug = false;

let loader;

const startLoader = () => {
  loader = setInterval(async () => {
    const enabled = await checkEnable();
    if (!enabled) stopLoader();

    const submissionStateElem = document.querySelector(".submissionState");
    if (submissionStateElem === null) return;

    const submissionState = submissionStateElem.textContent.trim();

    if (submissionState === RESULT_CATEGORY.RESULT_ACCEPTED) {
      stopLoader();
      log("Accepted problem detected, Starting upload...");
      const coplData = await parseData();
      await beginUpload(coplData);
    }
  }, 2000);
};

const stopLoader = () => {
  clearInterval(loader);
  loader = null;
};

const versionUpdate = async () => {
  log("Start Version Update");
  const stats = await updateLocalStorageStats();
  // Update Version
  stats.version = getVersion();
  await saveStats(stats);
  log("stats updated.", stats);
};

const beginUpload = async (coplData) => {
  console.log("Begin Upload with data", coplData);
  if (isNotEmpty(coplData)) {
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

    await uploadOneSolveProblemOnGit(coplData, () => {
      log("Uploaded complete!");
    });
  }
};

const currentUrl = window.location.href;

if (PROBLEM_URL_REGEX.test(currentUrl)) {
  log("start loader...");
  startLoader();
}
