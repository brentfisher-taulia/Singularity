import os
import sys
import fnmatch
import grequests
from glob import glob
from termcolor import colored
from callbacks import generate_callback
from singularity_request import get_json_response
import logfetch_base

DOWNLOAD_FILE_FORMAT = 'http://{0}:5051/files/download.json'
BROWSE_FOLDER_FORMAT = '{0}/sandbox/{1}/browse'

def download_live_logs(args):
  tasks = tasks_to_check(args)
  async_requests = []
  zipped_files = []
  all_logs = []
  sys.stderr.write(colored('Removing old service.log files', 'blue') + '\n')
  for f in glob('{0}/*service.log'.format(args.dest)):
    os.remove(f)
  sys.stderr.write(colored('Downloading current live log files', 'blue') + '\n')
  for task in tasks:
    metadata = files_json(args, task)
    uri = DOWNLOAD_FILE_FORMAT.format(metadata['slaveHostname'])
    for log_file in base_directory_files(args, task):
      logfile_name = '{0}-{1}'.format(task, log_file)
      if (args.logtype and logfetch_base.log_matches(log_file, args.logtype)) or not args.logtype:
        async_requests.append(
          grequests.AsyncRequest('GET',uri ,
            callback=generate_callback(uri, args.dest, logfile_name, args.chunk_size),
            params={'path' : '{0}/{1}/logs/{1}'.format(metadata['fullPathToRoot'], metadata['currentDirectory'], log_file)}
          )
        )
        if logfile_name.endswith('.gz'):
          zipped_files.append('{0}/{1}'.format(args.dest, logfile_name))
        all_logs.append('{0}/{1}'.format(args.dest, logfile_name.replace('.gz', '.log')))

    for log_file in logs_folder_files(args, task):
      logfile_name = '{0}-{1}'.format(task, log_file)
      if (args.logtype and logfetch_base.log_matches(log_file, args.logtype)) or not args.logtype:
        async_requests.append(
          grequests.AsyncRequest('GET',uri ,
            callback=generate_callback(uri, args.dest, logfile_name, args.chunk_size),
            params={'path' : '{0}/{1}/logs/{1}'.format(metadata['fullPathToRoot'], metadata['currentDirectory'], log_file)}
          )
        )
        if logfile_name.endswith('.gz'):
          zipped_files.append('{0}/{1}'.format(args.dest, logfile_name))
        all_logs.append('{0}/{1}'.format(args.dest, logfile_name.replace('.gz', '.log')))

  grequests.map(async_requests, stream=True, size=args.num_parallel_fetches)
  logfetch_base.unpack_logs(zipped_files)
  return all_logs

def tasks_to_check(args):
  if args.taskId:
    return [args.taskId]
  else:
    return logfetch_base.tasks_for_requests(args)

def files_json(args, task):
  uri = BROWSE_FOLDER_FORMAT.format(logfetch_base.base_uri(args), task)
  return get_json_response(uri)

def logs_folder_files(args, task):
  uri = BROWSE_FOLDER_FORMAT.format(logfetch_base.base_uri(args), task)
  files_json = get_json_response(uri, {'path' : '{0}/logs'.format(task)})
  if 'files' in files_json:
    files = files_json['files']
    return [f['name'] for f in files if logfetch_base.is_in_date_range(args, f['mtime'])]
  else:
    return [f['path'].rsplit('/')[-1] for f in files_json if logfetch_base.is_in_date_range(args, f['mtime'])]

def base_directory_files(args, task):
  uri = BROWSE_FOLDER_FORMAT.format(logfetch_base.base_uri(args), task)
  files_json = get_json_response(uri)
  if 'files' in files_json:
    files = files_json['files']
    return [f['name'] for f in files if valid_logfile(args, f)]
  else:
    return [f['path'].rsplit('/')[-1] for f in files_json if valid_logfile(args, f)]

def valid_logfile(args, fileData):
    is_in_range = logfetch_base.is_in_date_range(args, fileData['mtime'])
    not_a_directory = not fileData['mode'].startswith('d')
    is_a_logfile = fnmatch.fnmatch(fileData['name'], '*.log') or fnmatch.fnmatch(fileData['name'], '*.out') or fnmatch.fnmatch(fileData['name'], '*.err')
    return is_in_range and not_a_directory and is_a_logfile

