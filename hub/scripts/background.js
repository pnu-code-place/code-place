// TODO: This PROBLEM_URL_REGEX is defined in code_place/variables.js
// We should figure it out how to import the variables from there
const PROBLEM_URL_REGEX = /code.pusan.ac.kr\/problem\/\d+/;

function handleMessage(request, sender, sendResponse) {
  if (request && request.closeWebPage === true && request.isSuccess === true) {
    /* Set username */
    chrome.storage.local.set(
      { CodePlaceHub_username: request.username } /* , () => {
      window.localStorage.CodePlaceHub_username = request.username;
    } */
    );

    /* Set token */
    chrome.storage.local.set(
      { CodePlaceHub_token: request.token } /* , () => {
      window.localStorage[request.KEY] = request.token;
    } */
    );

    /* Close pipe */
    chrome.storage.local.set({ pipe_codeplacehub: false }, () => {
      console.log("Closed pipe.");
    });

    // chrome.tabs.getSelected(null, function (tab) {
    //   chrome.tabs.remove(tab.id);
    // });

    /* Go to onboarding for UX */
    const urlOnboarding = `chrome-extension://${chrome.runtime.id}/welcome.html`;
    chrome.tabs.create({ url: urlOnboarding, selected: true }); // creates new tab
  } else if (
    request &&
    request.closeWebPage === true &&
    request.isSuccess === false
  ) {
    alert("Something went wrong while trying to authenticate your profile!");
    chrome.tabs.getSelected(null, function (tab) {
      chrome.tabs.remove(tab.id);
    });
  }
  return true;
}

chrome.runtime.onMessage.addListener(handleMessage);

/**
 * Check URL and IF CURRENT URL IS PROBLEM PAGE,
 * Send message to scripts/code_place/code_place.js
 */
const handleProblemPageDetection = (tabId, url) => {
  if (PROBLEM_URL_REGEX.test(url)) {
    chrome.tabs.sendMessage(tabId, {
      action: "url_changed_to_problem_detail_page",
      url: url,
    });
    return true;
  }
  return false;
};

/**
 * Listen to tab update to cover the case if the user directly enters to the problem page
 */
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === "complete" && tab.url) {
    handleProblemPageDetection(tabId, tab.url);
  }
});
