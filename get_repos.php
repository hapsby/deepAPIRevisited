<?php



if (isset($_SERVER['argv'][3]) === false) {
    die("Run: php get_repos.php </path/to/repos> this_part number_of_parts\n");
}
chdir($_SERVER['argv'][1]);
$reposListFile = fopen('sorted_repos.txt', "r");
if ($reposListFile === false) {
    die("Can't find sorted_repos.txt.\n");
}

$thisPart = (int)$_SERVER['argv'][2] - 1;
$numberOfParts = (int)$_SERVER['argv'][3];
if ($numberOfParts < 1) {
    die("Must be at least one part.\n");
}
if ($thisPart < 0 || $thisPart >= $numberOfParts) {
    die("this_part must be in 1.." . $numberOfParts . "\n");
}

$externalRepos = [];
$externalReposFile = fopen('external_repos.txt', "r");
if ($externalReposFile !== false) {
	while (($externalReposLine = fgets($externalReposFile))) {
		$externalRepo = trim($externalReposLine);
		if ($externalRepo !== '') {
			$externalRepos[$externalRepo] = true;
		}
	}
}

while (($reposListLine = fgets($reposListFile))) {
    $repoUrl = trim($reposListLine);
    if ((crc32($repoUrl) % $numberOfParts) != $thisPart) {
        continue;
    }
    preg_match('`^git://github.com/([^/]+)/([^/]+).git$`', $repoUrl, $matches);
    if (isset($matches[2])) {
        $owner = $matches[1];
        $repo = $matches[2];
        $repoSubDirectory = $owner . '__' . $repo;
        $zipPath = $repoSubDirectory . '.7z';
        if (is_file($zipPath) === false && isset($externalRepos[$zipPath]) === false) {
            try {
                $baseGitUrl = 'https://api.github.com/repos/' . urlencode($owner) . '/' . urlencode($repo) . '/';
                cloneRepo($repoUrl, $repoSubDirectory);
                removeNonPythonFiles($repoSubDirectory);
                zipRepo($repoSubDirectory);
                exec ('rm -rf ' . escapeshellarg('./' . $repoSubDirectory));
            } catch (\Exception $e) {
                echo $repoUrl . " couldn't be downloaded: " . $e->getMessage() . "\n";
                clearstatcache();
                if (is_file($zipPath)) {
                    unlink($zipPath);
                }
            }
            sleep(6);
        }
    }
}


function zipRepo($subDirectory)
{
    $zipFilename = $subDirectory . '.7z';
    exec(
        '7z a ' . escapeshellarg($zipFilename) . ' ' . escapeshellarg($subDirectory) . ' 2>&1',
        $output,
        $exitCode
    );
    clearstatcache();
    if ($exitCode != 0 || !is_file($zipFilename)) {
	echo implode("\n", $output) . "\n";
        throw new \Exception("Couldn't create " . $zipFilename);
    }
}

function removeNonPythonFiles($subDirectory) {
    exec('find ' . escapeshellarg($subDirectory) . ' \\! -iname "*.py" -type f -exec rm -f {} \\;');
    exec('find ' . escapeshellarg($subDirectory) . ' -type d -empty -delete');
}

function cloneRepo($repoUrl, $repoSubDirectory)
{
    passthru(
        'git clone --depth 1 ' . escapeshellarg($repoUrl) . ' ' . escapeshellarg($repoSubDirectory),
        $exitCode
    );
    if ($exitCode != 0 || !is_dir($repoSubDirectory)) {
        throw new \Exception("Can't clone " . $repoUrl);
    }
}


