/**
 * Uploads a single solved problem to Git repository
 *
 * @async
 * @param {Object} coplData - Data of the solved problem
 * @param {string} coplData.summary - Summary content in markdown format
 * @param {string} coplData.directory - Directory path where the file will be uploaded
 * @param {string} coplData.summaryFileName - Summary file path
 * @param {string} coplData.sourceCodeFileName - Source code file path
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
    coplData.summary,
    coplData.directory,
    coplData.summaryFileName,
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
 * @param {string} summaryText - Content for the summary file
 * @param {string} directory - Directory path where the file will be uploaded
 * @param {string} summaryFileName - Summary file path
 * @param {string} sourceCodeFileName - Source code file path
 * @param {string} commitMessage - Message for the Git commit
 * @param {Function} [cb] - Optional callback function to execute after upload
 * @returns {Promise<void>} - Completes when upload is finished
 * @throws {Error} - If there's an issue during any GitHub operation
 */
const upload = async (
  token,
  hook,
  code,
  summaryText,
  directory,
  summaryFileName,
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
  const summary = await git.createBlob(
    summaryText,
    `${directory}/${summaryFileName}`
  );

  const treeSHA = await git.createTree(refSHA, [summary, sourceCode]);
  const commitSHA = await git.createCommit(commitMessage, treeSHA, refSHA);
  await git.updateHead(ref, commitSHA);

  updateObjectDatafromPath(
    stats.submission,
    `${hook}/${sourceCode.path}`,
    sourceCode.sha
  );
  updateObjectDatafromPath(
    stats.submission,
    `${hook}/${summary.path}`,
    summary.sha
  );

  await saveStats(stats);
  if (typeof cb === "function") {
    cb(stats.branches, directory);
  }
};
