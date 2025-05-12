/* global oAuth2 */
/* eslint no-undef: "error" */

// Setting up language using i18n
$(document).ready(() => {
  $("#main_caption").text(chrome.i18n.getMessage("main_caption"));
  $("#github_auth_request").text(chrome.i18n.getMessage("github_auth_request"));
  $("#github_auth_button_text").text(
    chrome.i18n.getMessage("github_auth_button_text")
  );
  $("#connected_repo_info").text(chrome.i18n.getMessage("connected_repo_info"));
  $("#reset_button_text").text(chrome.i18n.getMessage("reset_button_text"));
});

let action = false;

$("#authenticate").on("click", () => {
  if (action) {
    oAuth2.begin();
  }
});

$("#reset").on("click", () => {
  chrome.storage.local.clear(() => {
    log("Cleared all local storage");

    $("#auth_mode").show();
    $("#commit_mode").hide();
    $("#hook_mode").hide();
    action = true;
  });
});

/* Get URL for welcome page */
$("#welcome_URL").attr(
  "href",
  `chrome-extension://${chrome.runtime.id}/welcome.html`
);
$("#hook_URL").attr(
  "href",
  `chrome-extension://${chrome.runtime.id}/welcome.html`
);

chrome.storage.local.get("CodePlaceHub_token", (data) => {
  const token = data.CodePlaceHub_token;
  if (token === null || token === undefined) {
    action = true;
    $("#auth_mode").show();
  } else {
    // To validate user, load user object from GitHub.
    const AUTHENTICATION_URL = "https://api.github.com/user";

    const xhr = new XMLHttpRequest();
    xhr.addEventListener("readystatechange", function () {
      if (xhr.readyState === 4) {
        if (xhr.status === 200) {
          /* Show MAIN FEATURES */
          chrome.storage.local.get("mode_type", (data2) => {
            if (data2 && data2.mode_type === "commit") {
              $("#commit_mode").show();
              /* Get problem stats and repo link */
              chrome.storage.local.get(
                ["stats", "CodePlaceHub_hook"],
                (data3) => {
                  const CodePlaceHubHook = data3.CodePlaceHub_hook;
                  if (CodePlaceHubHook) {
                    $("#repo_url").html(
                      `<a target="_blank" style="color: cadetblue !important;" href="https://github.com/${CodePlaceHubHook}">${CodePlaceHubHook}</a>`
                    );
                  }
                }
              );
            } else {
              $("#hook_mode").show();
            }
          });
        } else if (xhr.status === 401) {
          // bad oAuth
          // reset token and redirect to authorization process again!
          chrome.storage.local.set({ CodePlaceHub_token: null }, () => {
            console.log("BAD oAuth!!! Redirecting back to oAuth process");
            action = true;
            $("#auth_mode").show();
          });
        }
      }
    });
    xhr.open("GET", AUTHENTICATION_URL, true);
    xhr.setRequestHeader("Authorization", `token ${token}`);
    xhr.send();
  }
});

/*
  초기에 활성화 데이터가 존재하는지 확인, 없으면 새로 생성, 있으면 있는 데이터에 맞게 버튼 조정
 */
chrome.storage.local.get("bjhEnable", (data4) => {
  if (data4.bjhEnable === undefined) {
    $("#onoffbox").prop("checked", true);
    chrome.storage.local.set(
      { bjhEnable: $("#onoffbox").is(":checked") },
      () => {}
    );
  } else {
    $("#onoffbox").prop("checked", data4.bjhEnable);
    chrome.storage.local.set(
      { bjhEnable: $("#onoffbox").is(":checked") },
      () => {}
    );
  }
});
/*
  활성화 버튼 클릭 시 storage에 활성 여부 데이터를 저장.
 */
$("#onoffbox").on("click", () => {
  chrome.storage.local.set(
    { bjhEnable: $("#onoffbox").is(":checked") },
    () => {}
  );
});
