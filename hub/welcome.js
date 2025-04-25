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
    $("#unlink a").on("click", () => {
      RepoManager.unlinkRepo();
      $("#unlink").hide();
      this.showSuccess(`
        <i class="huge blue check circle icon" style="margin-bottom: 0.5em"></i>
        <p>Successfully unlinked your current git repo. Please create/link a new hook.</p>
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
        this.showError(
          "Authorization error - Grant CodePlaceHub access to your GitHub account to continue (click CodePlaceHub extension on the top right to proceed)"
        );
        this.showHookMode();
        return;
      }

      chrome.storage.local.get("CodePlaceHub_hook", (repoData) => {
        const hook = repoData.CodePlaceHub_hook;
        if (!hook) {
          this.showError(
            "Improper Authorization error - Grant CodePlaceHub access to your GitHub account to continue (click CodePlaceHub extension on the top right to proceed)"
          );
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
   * Show commit mode UI elements
   */
  showCommitMode() {
    this.hideHookMode();
    $("#commit_mode").show();
  },

  /**
   * Display error message
   * @param {string} message - The error message to display
   */
  showError(message) {
    $("#success").hide();
    $("#error").html(message);
    $("#error").show();
  },

  /**
   * Display success message
   * @param {string} message - The success message to display
   */
  showSuccess(message) {
    $("#error").hide();
    $("#success").html(message);
    $("#success").show();
  },

  /**
   * Display repository link success message
   * @param {string} repoUrl - The repository URL
   * @param {string} repoName - The repository name
   */
  showRepoLinkSuccess(repoUrl, repoName) {
    this.showSuccess(`
      <i class="huge blue check circle icon" style="margin-bottom: 0.5em"></i>
      <p>Successfully linked <a target="blank" href="${repoUrl}">${repoName}</a> to CodePlaceHub.</p>
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
      <i class="huge blue check circle icon" style="margin-bottom: 0.5em"></i>
      <p>Successfully created <a target="blank" href="${repoUrl}">${repoName}</a>.</p>
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
      UI.showError(
        "No option selected - Pick an option from dropdown menu below that best suits you!"
      );
    } else if (!repoName) {
      UI.showError(
        "No repository name added - Enter the name of your repository!"
      );
      $("#name").focus();
    } else {
      UI.showSuccess("Attempting to create Hook... Please wait.");
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
        UI.showError(
          "Authorization error - Grant CodePlaceHub access to your GitHub account to continue (launch extension to proceed)"
        );
        return;
      }

      if (option === "new") {
        GitHubAPI.createRepo(token, repoName);
      } else {
        chrome.storage.local.get("CodePlaceHub_username", (userData) => {
          const username = userData.CodePlaceHub_username;
          if (!username) {
            UI.showError(
              "Improper Authorization error - Grant CodePlaceHub access to your GitHub account to continue (launch extension to proceed)"
            );
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
          `Error creating ${name} - Unable to modify repository. Try again later!`
        );
        break;
      case 400:
        UI.showError(
          `Error creating ${name} - Bad POST request, make sure you're not overriding any existing scripts`
        );
        break;
      case 401:
        UI.showError(
          `Error creating ${name} - Unauthorized access to repo. Try again later!`
        );
        break;
      case 403:
        UI.showError(
          `Error creating ${name} - Forbidden access to repository. Try again later!`
        );
        break;
      case 422:
        UI.showError(
          `Error creating ${name} - Unprocessable Entity. Repository may have already been created. Try Linking instead (select 2nd option).`
        );
        break;
      default:
        StorageManager.setModeType("commit");
        StorageManager.setRepoHook(response.full_name);
        UI.showRepoCreateSuccess(response.html_url, name);
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
          `Error linking <a target="blank" href="${repoUrl}">${repoName}</a> to CodePlaceHub. <br> This repository has been moved permenantly. Try creating a new one.`
        );
        break;
      case 403:
        UI.showError(
          `Error linking <a target="blank" href="${repoUrl}">${repoName}</a> to CodePlaceHub. <br> Forbidden action. Please make sure you have the right access to this repository.`
        );
        break;
      case 404:
        UI.showError(
          `Error linking <a target="blank" href="${repoUrl}">${repoName}</a> to CodePlaceHub. <br> Resource not found. Make sure you enter the right repository name.`
        );
        break;
      case 200:
        StorageManager.setModeType("commit");
        StorageManager.setRepoHook(response.full_name);
        StorageManager.setRepoUrl(response.html_url);
        RepoManager.initializeStats();
        UI.showRepoLinkSuccess(response.html_url, repoName);
        UI.hideHookMode();
        break;
      default:
        UI.showError(`Error linking repository. Unknown error (${status}).`);
        break;
    }

    $("#unlink").show();
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
