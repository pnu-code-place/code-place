/* Sync to local storage */
chrome.storage.local.get("isSync", (data) => {
  keys = [
    "CodePlaceHub_token",
    "CodePlaceHub_username",
    "pipe_codeplacehub",
    "stats",
    "CodePlaceHub_hook",
    "mode_type",
  ];
  if (!data || !data.isSync) {
    keys.forEach((key) => {
      chrome.storage.sync.get(key, (data) => {
        chrome.storage.local.set({ [key]: data[key] });
      });
    });
    chrome.storage.local.set({ isSync: true }, (data) => {
      // if (debug)
      console.log("CodePlaceHub Synced to local values");
    });
  } else {
    // if (debug)
    // console.log('Upload Completed. Local Storage status:', data);
    // if (debug)
    console.log("CodePlaceHub Local storage already synced!");
  }
});

/* stats 초기값이 없는 경우, 기본값을 생성하고 stats를 업데이트한다.
   만약 새로운 버전이 업데이트되었을 경우, 기존 submission은 업데이트를 위해 초기화 한다.
   (확인하기 어려운 다양한 케이스가 발생하는 것을 확인하여서 if 조건문을 복잡하게 하였다.)
*/
getStats().then((stats) => {
  if (isNull(stats)) stats = {};
  if (isNull(stats.version)) stats.version = "0.0.0";
  if (isNull(stats.branches) || stats.version !== getVersion())
    stats.branches = {};
  if (isNull(stats.submission) || stats.version !== getVersion())
    stats.submission = {};
  if (isNull(stats.problems) || stats.version !== getVersion())
    stats.problems = {};
  saveStats(stats);
});

/**
 * @author https://gist.github.com/sumitpore/47439fcd86696a71bf083ede8bbd5466
 * Chrome의 Local StorageArea에서 개체 가져오기
 * @param {string} key
 */
async function getObjectFromLocalStorage(key) {
  return new Promise((resolve, reject) => {
    try {
      chrome.storage.local.get(key, function (value) {
        resolve(value[key]);
      });
    } catch (ex) {
      reject(ex);
    }
  });
}

/**
 * @author https://gist.github.com/sumitpore/47439fcd86696a71bf083ede8bbd5466
 * Chrome의 Local StorageArea에 개체 저장
 * @param {*} obj
 */
async function saveObjectInLocalStorage(obj) {
  return new Promise((resolve, reject) => {
    try {
      chrome.storage.local.set(obj, function () {
        resolve();
      });
    } catch (ex) {
      reject(ex);
    }
  });
}

/**
 * @author https://gist.github.com/sumitpore/47439fcd86696a71bf083ede8bbd5466
 * Chrome Local StorageArea에서 개체 제거
 *
 * @param {string or array of string keys} keys
 */
async function removeObjectFromLocalStorage(keys) {
  return new Promise((resolve, reject) => {
    try {
      chrome.storage.local.remove(keys, function () {
        resolve();
      });
    } catch (ex) {
      reject(ex);
    }
  });
}

/**
 * Chrome의 Sync StorageArea에서 개체 가져오기
 * @param {string} key
 */
async function getObjectFromSyncStorage(key) {
  return new Promise((resolve, reject) => {
    try {
      chrome.storage.sync.get(key, function (value) {
        resolve(value[key]);
      });
    } catch (ex) {
      reject(ex);
    }
  });
}

/**
 * Chrome의 Sync StorageArea에 개체 저장
 * @param {*} obj
 */
async function saveObjectInSyncStorage(obj) {
  return new Promise((resolve, reject) => {
    try {
      chrome.storage.sync.set(obj, function () {
        resolve();
      });
    } catch (ex) {
      reject(ex);
    }
  });
}

/**
 * Chrome Sync StorageArea에서 개체 제거
 * @param {string or array of string keys} keys
 */
async function removeObjectFromSyncStorage(keys) {
  return new Promise((resolve, reject) => {
    try {
      chrome.storage.sync.remove(keys, function () {
        resolve();
      });
    } catch (ex) {
      reject(ex);
    }
  });
}

async function getToken() {
  return await getObjectFromLocalStorage("CodePlaceHub_token");
}

// async function getPipe() {
//   return await getObjectFromLocalStorage('pipe_codeplacehub');
// }

async function getGithubUsername() {
  return await getObjectFromLocalStorage("CodePlaceHub_username");
}

async function getStats() {
  return await getObjectFromLocalStorage("stats");
}

async function getHook() {
  return await getObjectFromLocalStorage("CodePlaceHub_hook");
}

async function getModeType() {
  return await getObjectFromLocalStorage("mode_type");
}

async function saveToken(token) {
  return await saveObjectInLocalStorage({ CodePlaceHub_token: token });
}

async function saveStats(stats) {
  return await saveObjectInLocalStorage({ stats });
}

/**
 * update stats from path recursively
 * ex) updateOptimizedStatsfromPath('_owner/_repo/백준/README.md', '1342259dssd') -> stats.submission.append({_owner: {_repo: {백준: {README.md: '1342259dssd'}}}})
 * updateOptimizedStatsfromPath('_owner/_repo/백준/1000.테스트/테스트.cpp', 'sfgbdksalf144') -> stats.submission.append({_owner: {_repo: {백준: {'1000.테스트': {'테스트.cpp': 'sfgbdksalf144'}}}}}})
 * updateOptimizedStatsfromPath('_owner/_repo/백준/1000.테스트/aaa/README.md', '123savvsvfffbb') -> stats.submission.append({_owner: {_repo: {백준: {'1000.테스트': {'aaa': {'README.md': '123savvsvfffbb'}}}}}})
 * @param {string} path - path to file
 * @param {string} sha - sha of file
 * @returns {Promise<void>}
 */
async function updateStatsSHAfromPath(path, sha) {
  const stats = await getStats();
  updateObjectDatafromPath(stats.submission, path, sha);
  await saveStats(stats);
}

function updateObjectDatafromPath(obj, path, data) {
  let current = obj;
  // split path into array and filter out empty strings
  const pathArray = path.split("/").filter((p) => p !== "");
  for (const path of pathArray.slice(0, -1)) {
    if (isNull(current[path])) {
      current[path] = {};
    }
    current = current[path];
  }
  current[pathArray.pop()] = data;
}

/**
 * get stats from path recursively
 * @param {string} path - path to file
 * @returns {Promise<string>} - sha of file
 */
async function getStatsSHAfromPath(path) {
  const stats = await getStats();
  return getObjectDatafromPath(stats.submission, path);
}

function getObjectDatafromPath(obj, path) {
  let current = obj;
  const pathArray = path.split("/").filter((p) => p !== "");
  for (const path of pathArray.slice(0, -1)) {
    if (isNull(current[path])) {
      return null;
    }
    current = current[path];
  }
  return current[pathArray.pop()];
}

/* github repo에 있는 모든 파일 목록을 가져와서 stats 갱신 */
async function updateLocalStorageStats() {
  const hook = await getHook();
  const token = await getToken();
  const git = new GitHub(hook, token);
  const stats = await getStats();
  const tree_items = [];
  await git.getTree().then((tree) => {
    tree.forEach((item) => {
      if (item.type === "blob") {
        tree_items.push(item);
      }
    });
  });
  const { submission } = stats;
  tree_items.forEach((item) => {
    updateObjectDatafromPath(submission, `${hook}/${item.path}`, item.sha);
  });
  const default_branch = await git.getDefaultBranchOnRepo();
  stats.branches[hook] = default_branch;
  await saveStats(stats);
  log("update stats", stats);
  return stats;
}
