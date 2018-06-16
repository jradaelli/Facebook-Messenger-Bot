import os


dataset = input("Do you want to create the dataset(y/n)?")
if dataset == 'y':
    try:
        [os.remove(file) for file in ('conversationData.txt',
                                      'conversationDictionary.npy', 'wordList.txt')]
    except:
        pass
    exec(open("createDataset.py").read())
wordemb = input("Do you want to create wordemb(y/n)?")
if wordemb == 'y':
    try:
        [os.remove(file)
         for file in ('Word2VecXTrain.npy', 'Word2VecYTrain.npy')]
    except:
        pass
    exec(open("Word2Vec.py").read())
seq2seq = input("Do you want to create seq2seq(y/n)?")
if seq2seq == 'y':
    try:
        [os.remove(file)
         for file in ('Seq2SeqXTrain.npy', 'Seq2SeqYTrain.npy')]
    except:
        pass
    exec(open("Seq2Seq.py").read())
