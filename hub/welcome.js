/**
 * CodePlace Hub - GitHub repository connection management module
 * This module handles linking and managing GitHub repositories with CodePlace
 */

/**
 * UI related elements management object
 * @namespace UI
 */
const UI = {
  /**
   * Initialize the UI
   * Sets up text elements, event listeners and checks mode type
   */
  init() {
    $(document).ready(() => {
      // Set up text elements with i18n translations
      this.updateText("main_caption", "main_caption");
      this.updateText("connect_repo_info", "connect_repo_info");
      this.updateText("repo_option_default", "repo_option_default");
      this.updateText("repo_option_new", "repo_option_new");
      this.updateText("repo_option_link", "repo_option_link");
      this.updateText("unlink_repo_info", "unlink_repo");
      this.updateText("unlink_repo_btn", "unlink_repo_button_text");

      this.setupEventListeners();
      this.checkModeType();
    });
  },

  /**
   * Update text elements with i18n translations
   * @param {string} elementId - The element ID to update
   * @param {string} messageKey - The i18n message key
   */
  updateText(elementId, messageKey) {
    $(`#${elementId}`).text(chrome.i18n.getMessage(messageKey));
  },

  /**
   * Set up event listeners for UI elements
   */
  setupEventListeners() {
    // Dropdown change event
    $("#type").on("change", function () {
      $("#hook_button").attr("disabled", !this.value);
    });

    // Get Started button click event
    $("#hook_button").on("click", RepoManager.handleCreateOrLink);

    // Unlink link click event
    $("#unlink_repo_btn").on("click", () => {
      RepoManager.unlinkRepo();
      $("#unlink").hide();
      this.showSuccess(`
        <p>${chrome.i18n.getMessage("repo_unlink_success")}</p>
      `);
    });
  },

  /**
   * Check mode type and apply appropriate settings
   */
  checkModeType() {
    chrome.storage.local.get("mode_type", (data) => {
      const mode = data.mode_type;
      if (mode && mode === "commit") {
        this.checkRepoAccess();
        this.hideHookMode();
      } else {
        this.showHookMode();
      }
    });
  },

  /**
   * Check repository access permissions
   */
  checkRepoAccess() {
    chrome.storage.local.get("CodePlaceHub_token", (data) => {
      const token = data.CodePlaceHub_token;
      if (!token) {
        this.showError(chrome.i18n.getMessage("error_improper_auth"));
        this.showHookMode();
        return;
      }

      chrome.storage.local.get("CodePlaceHub_hook", (repoData) => {
        const hook = repoData.CodePlaceHub_hook;
        if (!hook) {
          this.showError(chrome.i18n.getMessage("error_improper_auth"));
          this.showHookMode();
          return;
        }

        GitHubAPI.linkRepo(token, hook);
      });
    });
  },

  /**
   * Show hook mode UI elements
   */
  showHookMode() {
    $("#hook_mode").show();
    this.updateText("connect_repo_info", "connect_repo_info");
  },

  /**
   * Hide hook mode UI elements
   */
  hideHookMode() {
    $("#hook_mode").hide();
  },

  /**
   * Display error message
   * @param {HTMLElement} htmlContent - The HTML content to display as an error message
   */
  showError(htmlContent) {
    $("#success").hide();
    $("#error_detail").html(htmlContent);
    $("#error").show();
  },

  /**
   * Display success message
   * @param {HTMLElement} htmlContent - The HTML content to display as a success message
   */
  showSuccess(htmlContent) {
    $("#error").hide();
    $("#success_detail").html(htmlContent);
    $("#success").show();
  },

  /**
   * Display repository link success message
   * @param {string} repoUrl - The repository URL
   * @param {string} repoName - The repository name
   */
  showRepoLinkSuccess(repoUrl, repoName) {
    this.showSuccess(`
      <p>${chrome.i18n.getMessage("repo_link_success")}</p>
      <p>${chrome.i18n.getMessage("recommend_refresh")}</p>
    `);
    $("#unlink").show();
  },

  /**
   * Display repository creation success message
   * @param {string} repoUrl - The repository URL
   * @param {string} repoName - The repository name
   */
  showRepoCreateSuccess(repoUrl, repoName) {
    this.showSuccess(`
      <p>${chrome.i18n.getMessage("repo_create_success")}</p>
      <p>${chrome.i18n.getMessage("recommend_refresh")}</p>
    `);
    $("#unlink").show();
    $("#hook_mode").show();
  },
};

/**
 * Repository management object
 * @namespace RepoManager
 */
const RepoManager = {
  /**
   * Get selected option value (create new or link existing repository)
   * @returns {string} The selected option value
   */
  getOption() {
    return $("#type").val();
  },

  /**
   * Get repository name from input
   * @returns {string} The repository name
   */
  getRepositoryName() {
    return $("#name").val().trim();
  },

  /**
   * Handle repository creation or linking
   */
  handleCreateOrLink() {
    const option = RepoManager.getOption();
    const repoName = RepoManager.getRepositoryName();

    if (!option) {
      UI.showError(chrome.i18n.getMessage("error_no_option_selected"));
    } else if (!repoName) {
      UI.showError(chrome.i18n.getMessage("error_no_repo_name"));
      $("#name").focus();
    } else {
      RepoManager.processRequest(option, repoName);
    }
  },

  /**
   * Process repository request (create or link)
   * @param {string} option - The option type ('new' or 'link')
   * @param {string} repoName - The repository name
   */
  processRequest(option, repoName) {
    chrome.storage.local.get("CodePlaceHub_token", (data) => {
      const token = data.CodePlaceHub_token;
      if (!token) {
        UI.showError(chrome.i18n.getMessage("error_improper_auth"));
        return;
      }

      if (option === "new") {
        GitHubAPI.createRepo(token, repoName);
      } else {
        chrome.storage.local.get("CodePlaceHub_username", (userData) => {
          const username = userData.CodePlaceHub_username;
          if (!username) {
            UI.showError(chrome.i18n.getMessage("error_improper_auth"));
            return;
          }
          GitHubAPI.linkRepo(token, `${username}/${repoName}`);
        });
      }
    });
  },

  /**
   * Unlink repository from CodePlaceHub
   */
  unlinkRepo() {
    StorageManager.setModeType("hook");
    StorageManager.setRepoHook(null);
    UI.showHookMode();
  },

  /**
   * Initialize statistics for the repository
   */
  initializeStats() {
    const stats = {
      version: chrome.runtime.getManifest().version,
      submission: {},
    };
    chrome.storage.local.set({ stats });
  },
};

/**
 * GitHub API integration object
 * @namespace GitHubAPI
 */
const GitHubAPI = {
  /**
   * Create a new GitHub repository
   * @param {string} token - GitHub access token
   * @param {string} name - Repository name
   */
  createRepo(token, name) {
    const url = "https://api.github.com/user/repos";
    const data = JSON.stringify({
      name,
      private: true,
      auto_init: true,
      description:
        "This is an auto push repository of algorithm solutions in Code Place pushed by CodePlaceHub",
    });

    const xhr = new XMLHttpRequest();
    xhr.addEventListener("readystatechange", function () {
      if (xhr.readyState === 4) {
        const response = JSON.parse(xhr.responseText);
        GitHubAPI.handleCreateRepoResponse(response, xhr.status, name, token);
      }
    });

    RepoManager.initializeStats();

    xhr.open("POST", url, true);
    xhr.setRequestHeader("Authorization", `token ${token}`);
    xhr.setRequestHeader("Accept", "application/vnd.github.v3+json");
    xhr.send(data);
  },

  /**
   * Handle repository creation response
   * @param {Object} response - API response object
   * @param {number} status - HTTP status code
   * @param {string} name - Repository name
   * @param {string} token - GitHub access token
   */
  handleCreateRepoResponse(response, status, name, token) {
    switch (status) {
      case 304:
        UI.showError(
          `Error creating ${name} - ${chrome.i18n.getMessage(
            "error_unable_to_modify_repo"
          )}`
        );
        break;
      case 400:
        UI.showError(
          `Error creating ${name} - ${chrome.i18n.getMessage(
            "error_bad_request"
          )}`
        );
        break;
      case 401:
        UI.showError(
          `Error creating ${name} - ${chrome.i18n.getMessage(
            "error_unauthorized_access_to_repo"
          )}`
        );
        break;
      case 403:
        UI.showError(
          `Error creating ${name} - ${chrome.i18n.getMessage(
            "error_forbidden_access_to_repo"
          )}`
        );
        break;
      case 422:
        UI.showError(
          `Error creating ${name} - ${chrome.i18n.getMessage(
            "error_unprocessable_entity"
          )}`
        );
        break;
      default:
        StorageManager.setModeType("commit");
        StorageManager.setRepoHook(response.full_name);
        UI.showRepoCreateSuccess(response.html_url, name);
        UI.hideHookMode();
        break;
    }
  },

  /**
   * Link an existing repository
   * @param {string} token - GitHub access token
   * @param {string} fullRepoName - Full repository name (username/repo)
   */
  linkRepo(token, fullRepoName) {
    const url = `https://api.github.com/repos/${fullRepoName}`;

    const xhr = new XMLHttpRequest();
    xhr.addEventListener("readystatechange", function () {
      if (xhr.readyState === 4) {
        const response = JSON.parse(xhr.responseText);
        GitHubAPI.handleLinkRepoResponse(
          response,
          xhr.status,
          fullRepoName,
          token
        );
      }
    });

    xhr.open("GET", url, true);
    xhr.setRequestHeader("Authorization", `token ${token}`);
    xhr.setRequestHeader("Accept", "application/vnd.github.v3+json");
    xhr.send();
  },

  /**
   * Handle repository link response
   * @param {Object} response - API response object
   * @param {number} status - HTTP status code
   * @param {string} fullRepoName - Full repository name
   * @param {string} token - GitHub access token
   */
  handleLinkRepoResponse(response, status, fullRepoName, token) {
    const repoName = fullRepoName.split("/")[1] || fullRepoName;
    const repoUrl = `https://github.com/${fullRepoName}`;

    switch (status) {
      case 301:
        UI.showError(
          `Error linking <a target="blank" href="${repoUrl}">${repoName}</a> - ${chrome.i18n.getMessage(
            "error_moved_permanently"
          )}`
        );
        break;
      case 403:
        UI.showError(
          `Error linking <a target="blank" href="${repoUrl}">${repoName}</a> - ${chrome.i18n.getMessage(
            "error_forbidden_access_to_repo"
          )}`
        );
        break;
      case 404:
        UI.showError(
          `Error linking <a target="blank" href="${repoUrl}">${repoName}</a> - ${chrome.i18n.getMessage(
            "error_repo_not_found"
          )}`
        );
        break;
      case 200:
        StorageManager.setModeType("commit");
        StorageManager.setRepoHook(response.full_name);
        StorageManager.setRepoUrl(response.html_url);
        RepoManager.initializeStats();
        UI.showRepoLinkSuccess(response.html_url, repoName);
        UI.hideHookMode();
        $("#unlink").show();
        break;
      default:
        UI.showError(`Error linking repository. Unknown error (${status}).`);
        break;
    }
  },
};

/**
 * Storage management object
 * @namespace StorageManager
 */
const StorageManager = {
  /**
   * Set mode type (hook or commit)
   * @param {string} modeType - Mode type ('hook' or 'commit')
   */
  setModeType(modeType) {
    chrome.storage.local.set({ mode_type: modeType }, () => {
      console.log(`Mode type set to: ${modeType}`);
    });
  },

  /**
   * Set repository hook
   * @param {string|null} repoFullName - Full repository name or null to unlink
   */
  setRepoHook(repoFullName) {
    chrome.storage.local.set({ CodePlaceHub_hook: repoFullName }, () => {
      console.log(
        repoFullName
          ? "Successfully set new repo hook"
          : "Defaulted repo hook to NONE"
      );
    });
  },

  /**
   * Set repository URL
   * @param {string} url - Repository URL
   */
  setRepoUrl(url) {
    chrome.storage.local.set({ repo: url }, () => {
      console.log(`Repository URL set to: ${url}`);
    });
  },
};

// Initialize application
UI.init();
