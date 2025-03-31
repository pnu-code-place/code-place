/**
 * Uploads a single solved problem to Git repository
 *
 * @async
 * @param {Object} coplData - Data of the solved problem
 * @param {string} coplData.readme - README content in markdown format
 * @param {string} coplData.directory - Directory path where the file will be uploaded
 * @param {string} coplData.commitMessage - Message for the Git commit
 * @param {Function} [cb] - Optional callback function to execute after upload
 * @returns {Promise<void|Object>} - Result of the upload operation or void if token/hook is null
 * @throws {Error} - If there's an issue during the upload process
 */
const uploadOneSolveProblemOnGit = async (coplData, cb) => {
  const token = await getToken();
  const hook = await getHook();
  if (isNull(token) || isNull(hook)) {
    console.error("token or hook is null", token, hook);
    return;
  }
  return upload(
    token,
    hook,
    coplData.code,
    coplData.readme,
    coplData.directory,
    coplData.sourceCodeFileName,
    coplData.commitMessage,
    cb
  );
};

/**
 * Performs the actual upload to GitHub repository
 *
 * @async
 * @param {string} token - GitHub authentication token
 * @param {string} hook - GitHub repository reference
 * @param {string} readmeText - Content for the README.md file
 * @param {string} directory - Directory path where the file will be uploaded
 * @param {string} commitMessage - Message for the Git commit
 * @param {Function} [cb] - Optional callback function to execute after upload
 * @returns {Promise<void>} - Completes when upload is finished
 * @throws {Error} - If there's an issue during any GitHub operation
 */
const upload = async (
  token,
  hook,
  code,
  readmeText,
  directory,
  sourceCodeFileName,
  commitMessage,
  cb
) => {
  const git = new GitHub(hook, token);
  const stats = await getStats();
  let default_branch = stats.branches[hook];
  if (isNull(default_branch)) {
    default_branch = await git.getDefaultBranchOnRepo();
    stats.branches[hook] = default_branch;
  }
  const { refSHA, ref } = await git.getReference(default_branch);
  const sourceCode = await git.createBlob(
    code,
    `${directory}/${sourceCodeFileName}`
  );
  const readme = await git.createBlob(readmeText, `${directory}/README.md`);
  const treeSHA = await git.createTree(refSHA, [readme, sourceCode]);
  const commitSHA = await git.createCommit(commitMessage, treeSHA, refSHA);
  await git.updateHead(ref, commitSHA);

  updateObjectDatafromPath(
    stats.submission,
    `${hook}/${sourceCode.path}`,
    sourceCode.sha
  );
  updateObjectDatafromPath(
    stats.submission,
    `${hook}/${readme.path}`,
    readme.sha
  );
  await saveStats(stats);
  if (typeof cb === "function") {
    cb(stats.branches, directory);
  }
};
