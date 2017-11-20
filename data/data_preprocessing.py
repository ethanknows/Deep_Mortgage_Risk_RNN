import argparse
import os
import numpy as np

parser = argparse.ArgumentParser(description='Generate random buckets. ')
parser.add_argument('--dataset', help='prime/subprime/all')
args = parser.parse_args()

def longitudinal_separation(lValue, tValue, sep=[121,281,287,306]):
	###retun the length in train/valid/test
	len_train = min(max(sep[1]-tValue,0),lValue)
	len_valid = min(max(sep[2]-tValue,0),max(tValue+lValue-sep[1],0),lValue,sep[2]-sep[1])
	len_test = min(max(tValue+lValue-sep[2],0),lValue)
	return np.array([len_train,len_valid,len_test], dtype='int16')

path = os.path.expanduser('~')

if args.dataset == 'subprime':
	path_subprime = os.path.join(path, 'data/RNNdata')
	path_src = os.path.join(path_subprime, 'subprime')
	path_tgt = os.path.join(path_subprime, 'subprime_new')
	###use bucket size [50, 100, 150, 200]
	###num of bucket [2800, 500, 120, 15]
	###~4000 loan in each bucket
	num_bucket = {50:2800, 100:500, 150:120, 200:15}

	for lValue in os.listdir(path_src):
		bucket = (int(lValue) + 49) // 50 * 50
		for tValue in os.listdir(os.path.join(path_src,lValue)):
			len_sep = longitudinal_separation(lValue=int(lValue), tValue=int(tValue))

			path_i = os.path.join(path_src, lValue, tValue)
			X_int_list = []
			X_float_list = []
			outcome_list = []
			loanID_list = []
			for file in os.listdir(path_i):
				if file.startswith('X_data_np_int'):
					X_int_list.append(file)
				elif file.startswith('X_data_np_float'):
					X_float_list.append(file)
				elif file.startswith('outcome'):
					outcome_list.append(file)
				elif file.startswith('loanID'):
					loanID_list.append(file)
			X_int_list = sorted(X_int_list)
			X_float_list = sorted(X_float_list)
			outcome_list = sorted(outcome_list)
			loanID_list = sorted(loanID_list)
			num_file = len(loanID_list)

			for idx_src in range(num_file):
				if idx_src % 10 == 0:
					print('Processing files in %s: %d / %d' %(path_i, idx_src, num_file), end='\r')
				loanID = np.load(os.path.join(path_i, loanID_list[idx_src]))
				loanID = loanID.reshape((-1, int(lValue)))[:,0]

				X_float = np.load(os.path.join(path_i, X_float_list[idx_src]))
				X_float = X_float.reshape((-1, int(lValue), 54))

				X_int = np.load(os.path.join(path_i, X_int_list[idx_src]))
				X_int = X_int.reshape((-1, int(lValue), 239))

				outcome = np.load(os.path.join(path_i, outcome_list[idx_src]))
				outcome = outcome.reshape((-1, int(lValue)))

				idx_tgt = np.random.choice(num_bucket[bucket], len(loanID))

				for i in range(len(loanID)):
					idx = idx_tgt[i]

					path_loanID = os.path.join(path_tgt, 'loanID_np_%d_%d.npy' %(bucket, idx))
					if os.path.exists(path_loanID):
						loanID_new = np.load(path_loanID)
						loanID_new = np.append(loanID_new, [loanID[i]], axis=0)
					else:
						loanID_new = np.array([loanID[i]], dtype=loanID.dtype)
					np.save(path_loanID, loanID_new)
					loanID_new = None

					path_X_int = os.path.join(path_tgt, 'X_data_np_int_%d_%d.npy' %(bucket, idx))
					if os.path.exists(path_X_int):
						X_int_new = np.load(path_X_int)
						X_int_new = np.append(X_int_new, [np.lib.pad(X_int[i], ((0, bucket-int(lValue)),(0,0)), 'constant')], axis=0)
					else:
						X_int_new = np.array([np.lib.pad(X_int[i], ((0, bucket-int(lValue)),(0,0)), 'constant')], dtype=X_int.dtype)
					np.save(path_X_int, X_int_new)
					X_int_new = None

					path_X_float = os.path.join(path_tgt, 'X_data_np_float_%d_%d.npy' %(bucket, idx))
					if os.path.exists(path_X_float):
						X_float_new = np.load(path_X_float)
						X_float_new = np.append(X_float_new, [np.lib.pad(X_float[i], ((0, bucket-int(lValue)),(0,0)), 'constant')], axis=0)
					else:
						X_float_new = np.array([np.lib.pad(X_float[i], ((0, bucket-int(lValue)),(0,0)), 'constant')], dtype=X_float.dtype)
					np.save(path_X_float, X_float_new)
					X_float_new = None

					path_outcome = os.path.join(path_tgt, 'outcome_data_np_%d_%d.npy' %(bucket, idx))
					if os.path.exists(path_outcome):
						outcome_new = np.load(path_outcome)
						outcome_new = np.append(outcome_new, [np.lib.pad(outcome[i], (0, bucket-int(lValue)), 'constant')], axis=0)
					else:
						outcome_new = np.array([np.lib.pad(outcome[i], (0, bucket-int(lValue)), 'constant')], dtype=outcome.dtype)
					np.save(path_outcome, outcome_new)
					outcome_new = None

					path_tDimSplit = os.path.join(path_tgt, 'tDimSplit_np_%d_%d.npy' %(bucket, idx))
					if os.path.exists(path_tDimSplit):
						tDimSplit_new = np.load(path_tDimSplit)
						tDimSplit_new = np.append(tDimSplit_new, [len_sep], axis=0)
					else:
						tDimSplit_new = np.array([len_sep], dtype=len_sep.dtype)
					np.save(path_tDimSplit, tDimSplit_new)
					tDimSplit_new = None
			print('%s Completed! ' %path_i)

elif args.dataset == 'prime':
	raise ValueError('Not Implemented!')
elif args.dataset == 'all':
	raise ValueError('Not Implemented!')
else:
	raise ValueError('Dataset Not Found! ')