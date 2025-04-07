/* 
    (needs patch) 
    IMPLEMENTATION OF AUTHENTICATION ROUTE AFTER REDIRECT FROM GITHUB.
*/

const localAuth = {
  /**
   * Initialize
   */
  init() {
    this.KEY = "CodePlaceHub_token";
    // TODO: Change ACCESS_TOKEN_URL to the correct one. This is for testing.
    this.ACCESS_TOKEN_URL = "http://localhost:8081/api/token/issue";
    this.AUTHORIZATION_URL = "https://github.com/login/oauth/authorize";
    this.REDIRECT_URL = "https://github.com/"; // for example, https://github.com
    this.SCOPES = ["repo"];
  },

  /**
   * Parses Access Code
   *
   * @param url The url containing the access code.
   */
  parseAccessCode(url) {
    if (url.match(/\?error=(.+)/)) {
      chrome.tabs.getCurrent(function (tab) {
        chrome.tabs.remove(tab.id, function () {});
      });
    } else {
      // eslint-disable-next-line
      const accessCode = url.match(/\?code=([\w\/\-]+)/);
      if (accessCode) {
        this.requestToken(accessCode[1]);
      }
    }
  },

  /**
   * Request Token
   *
   * @param code The access code returned by provider.
   */
  async requestToken(code) {
    try {
      const response = await fetch(this.ACCESS_TOKEN_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({ code }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error("Failed to get token:", errorData);
        chrome.runtime.sendMessage({
          closeWebPage: true,
          isSuccess: false,
        });
      }

      const data = await response.json();
      this.finish(data.access_token);
    } catch (error) {
      console.error("Error fetching token:", error);
    }
  },

  /**
   * Finish
   *
   * @param token The OAuth2 token given to the application from the provider.
   */
  finish(token) {
    /* Get username */
    // To validate user, load user object from GitHub.
    const AUTHENTICATION_URL = "https://api.github.com/user";

    const xhr = new XMLHttpRequest();
    xhr.addEventListener("readystatechange", () => {
      if (xhr.readyState === 4) {
        if (xhr.status === 200) {
          const username = JSON.parse(xhr.responseText).login;
          chrome.runtime.sendMessage({
            closeWebPage: true,
            isSuccess: true,
            token,
            username,
            KEY: this.KEY,
          });
        }
      }
    });
    xhr.open("GET", AUTHENTICATION_URL, true);
    xhr.setRequestHeader("Authorization", `token ${token}`);
    xhr.send();
  },
};

localAuth.init(); // load params.
const link = window.location.href;

/* Check for open pipe */
if (window.location.host === "github.com") {
  chrome.storage.local.get("pipe_codeplacehub", (data) => {
    if (data && data.pipe_codeplacehub) {
      localAuth.parseAccessCode(link);
    }
  });
}
