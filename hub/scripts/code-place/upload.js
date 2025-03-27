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
    coplData.readme,
    coplData.directory,
    coplData.commitMessage,
    cb
  );
};

const upload = async (
  token,
  hook,
  readmeText,
  directory,
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
  const readme = await git.createBlob(readmeText, `${directory}/README.md`);
  const treeSHA = await git.createTree(refSHA, [readme]);
  const commitSHA = await git.createCommit(commitMessage, treeSHA, refSHA);
  await git.updateHead(ref, commitSHA);

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
