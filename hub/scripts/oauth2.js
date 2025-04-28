// eslint-disable-next-line no-unused-vars
const oAuth2 = {
  /**
   * Initialize
   */
  init() {
    this.KEY = "CodePlaceHub_token";
    // TODO: Change ACCESS_TOKEN_URL to the correct one. This is for testing.
    this.ACCESS_TOKEN_URL = "https://hub-auth.copl-dev.site/api/token/issue";
    this.AUTHORIZATION_URL = "https://github.com/login/oauth/authorize";
    this.CLIENT_ID = "Ov23liGMeecEJnH8nRfD"; // Code Place Hub OAuth App ID
    this.REDIRECT_URL = "https://github.com/"; // for example, https://github.com
    this.SCOPES = ["repo"];
  },

  /**
   * Begin
   */
  begin() {
    this.init(); // secure token params.

    let url = `${this.AUTHORIZATION_URL}?client_id=${this.CLIENT_ID}&redirect_uri${this.REDIRECT_URL}&scope=`;

    for (let i = 0; i < this.SCOPES.length; i += 1) {
      url += this.SCOPES[i];
    }

    chrome.storage.local.set({ pipe_codeplacehub: true }, () => {
      // opening pipe temporarily

      chrome.tabs.create({ url, selected: true }, function () {
        window.close();
        chrome.tabs.getCurrent(function (tab) {
          // chrome.tabs.remove(tab.id, function () {});
        });
      });
    });
  },
};
