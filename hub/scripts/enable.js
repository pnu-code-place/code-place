/* 
    비활성화시 작동되지 않게 함
    가독성을 위해 따로 파일 분리함
*/
async function checkEnable() {
  const enable = await getObjectFromLocalStorage("bjhEnable");
  if (!enable) writeEnableMsgOnLog();
  return enable;
}

function writeEnableMsgOnLog() {
  const errMsg = "확장이 활성화되지 않았습니다. 확장을 활성화하고 시도해주세요";
  console.log(errMsg);
}

/**
 * Check if the local storage contains the required keys for uploading
 * @returns {Promise<boolean>} - True if all required keys are present, false otherwise
 */
const checkLocalStorage = async () => {
  const keys = [
    "CodePlaceHub_token",
    "CodePlaceHub_username",
    "CodePlaceHub_hook",
  ];

  for (const key of keys) {
    const value = await getObjectFromLocalStorage(key);
    if (!value) {
      log(`Local storage key "${key}" is missing.`);
      return false;
    }
  }

  return true;
};
