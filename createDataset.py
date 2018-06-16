import pandas as pd
import numpy as np
import os
import re
from datetime import datetime
import pysrt
import nltk

# nltk.download('punkt')

# personName = input('Enter your full name: ')
# fbData = input('Do you have Facebook data to parse through (y/n)?')
# googleData = input('Do you have Google Hangouts data to parse through (y/n)?')
# linkedInData = input('Do you have LinkedIn data to parse through (y/n)?')
# whatsAppData = input('Do you have whatsAppData to parse through (y/n)?')
subtitles = input('Do you have subtitles to parse through (y/n)?')


def getWhatsAppData():
    df = pd.read_csv('whatsapp_chats.csv')
    responseDictionary = dict()
    receivedMessages = df[df['From'] != personName]
    sentMessages = df[df['From'] == personName]
    combined = pd.concat([sentMessages, receivedMessages])
    otherPersonsMessage, myMessage = "", ""
    firstMessage = True
    for index, row in combined.iterrows():
        if (row['From'] != personName):
            if myMessage and otherPersonsMessage:
                otherPersonsMessage = cleanMessage(otherPersonsMessage)
                myMessage = cleanMessage(myMessage)
                responseDictionary[otherPersonsMessage.rstrip()
                                   ] = myMessage.rstrip()
                otherPersonsMessage, myMessage = "", ""
            otherPersonsMessage = otherPersonsMessage + \
                str(row['Content']) + " "
        else:
            if (firstMessage):
                firstMessage = False
                # Don't include if I am the person initiating the convo
                continue
            myMessage = myMessage + str(row['Content']) + " "
    return responseDictionary


def getGoogleHangoutsData():
    # Putting all the file names in a list
    allFiles = []
    # Edit these file and directory names if you have them saved somewhere else
    for filename in os.listdir('GoogleTextForm'):
        if filename.endswith(".txt"):
            allFiles.append('GoogleTextForm/' + filename)

    # The key is the other person's message, and the value is my response
    responseDictionary = dict()
    # Going through each file, and recording everyone's messages to me, and my responses
    for currentFile in allFiles:
        myMessage, otherPersonsMessage, currentSpeaker = "", "", ""
        openedFile = open(currentFile, 'r')
        allLines = openedFile.readlines()
        for index, lines in enumerate(allLines):
            # The sender's name is separated by < and >
            leftBracket = lines.find('<')
            rightBracket = lines.find('>')

            # Find messages that I sent
            if (lines[leftBracket + 1:rightBracket] == personName):
                if not myMessage:
                    # Want to find the first message that I send (if I send multiple in a row)
                    startMessageIndex = index - 1
                myMessage += lines[rightBracket + 1:]

            elif myMessage:
                # Now go and see what message the other person sent by looking at previous messages
                for counter in range(startMessageIndex, 0, -1):
                    currentLine = allLines[counter]
                    # In case the message above isn't in the right format
                    if (currentLine.find('<') < 0 or currentLine.find('>') < 0):
                        myMessage, otherPersonsMessage, currentSpeaker = "", "", ""
                        break
                    if not currentSpeaker:
                        # The first speaker not named me
                        currentSpeaker = currentLine[currentLine.find(
                            '<') + 1:currentLine.find('>')]
                    elif (currentSpeaker != currentLine[currentLine.find('<') + 1:currentLine.find('>')]):
                        # A different person started speaking, so now I know that the first person's message is done
                        otherPersonsMessage = cleanMessage(otherPersonsMessage)
                        myMessage = cleanMessage(myMessage)
                        responseDictionary[otherPersonsMessage] = myMessage
                        break
                    otherPersonsMessage = currentLine[currentLine.find(
                        '>') + 1:] + otherPersonsMessage
                myMessage, otherPersonsMessage, currentSpeaker = "", "", ""
    return responseDictionary


def getFacebookData():
    responseDictionary = dict()
    fbFile = open('fbMessages.txt', 'r')
    allLines = fbFile.readlines()
    myMessage, otherPersonsMessage, currentSpeaker = "", "", ""
    for index, lines in enumerate(allLines):
        rightBracket = lines.find(']') + 2
        justMessage = lines[rightBracket:]
        colon = justMessage.find(':')
        # Find messages that I sent
        if (justMessage[:colon] == personName):
            if not myMessage:
                # Want to find the first message that I send (if I send multiple in a row)
                startMessageIndex = index - 1
            myMessage += justMessage[colon + 2:]

        elif myMessage:
            # Now go and see what message the other person sent by looking at previous messages
            for counter in range(startMessageIndex, 0, -1):
                currentLine = allLines[counter]
                rightBracket = currentLine.find(']') + 2
                justMessage = currentLine[rightBracket:]
                colon = justMessage.find(':')
                if not currentSpeaker:
                    # The first speaker not named me
                    currentSpeaker = justMessage[:colon]
                elif (currentSpeaker != justMessage[:colon] and otherPersonsMessage):
                    # A different person started speaking, so now I know that the first person's message is done
                    otherPersonsMessage = cleanMessage(otherPersonsMessage)
                    myMessage = cleanMessage(myMessage)
                    responseDictionary[otherPersonsMessage] = myMessage
                    break
                otherPersonsMessage = justMessage[colon +
                                                  2:] + otherPersonsMessage
            myMessage, otherPersonsMessage, currentSpeaker = "", "", ""
    return responseDictionary


def getLinkedInData():
    df = pd.read_csv('Inbox.csv')

    def dateTimeConverter(x): return datetime.strptime(
        x, '%B %d, %Y, %I:%M %p')
    responseDictionary = dict()
    peopleContacted = df['From'].unique().tolist()
    for person in peopleContacted:
        receivedMessages = df[df['From'] == person]
        sentMessages = df[df['To'] == person]
        if (len(sentMessages) == 0 or len(receivedMessages) == 0):
            # There was no actual conversation
            continue
        combined = pd.concat([sentMessages, receivedMessages])
        combined['Date'] = combined['Date'].apply(dateTimeConverter)
        combined = combined.sort(['Date'])
        otherPersonsMessage, myMessage = "", ""
        firstMessage = True
        for index, row in combined.iterrows():
            if (row['From'] != personName):
                if myMessage and otherPersonsMessage:
                    otherPersonsMessage = cleanMessage(otherPersonsMessage)
                    myMessage = cleanMessage(myMessage)
                    responseDictionary[otherPersonsMessage.rstrip(
                    )] = myMessage.rstrip()
                    otherPersonsMessage, myMessage = "", ""
                otherPersonsMessage = otherPersonsMessage + \
                    row['Content'] + " "
            else:
                if (firstMessage):
                    firstMessage = False
                    # Don't include if I am the person initiating the convo
                    continue
                myMessage = myMessage + str(row['Content']) + " "
    return responseDictionary


def getSubtitles():
    PATH_FILE = os.path.join("..", "friends")
    file_list = os.listdir(PATH_FILE)
    qa_dict = dict()
    for one_file in file_list:
        if one_file.endswith(".srt"):
            subs = pysrt.open(os.path.join(
                PATH_FILE, one_file), encoding='iso-8859-1')
            part_train = subs.slice(starts_after={'minutes': 2, 'seconds': 30}, ends_before={
                                    'minutes': 19, 'seconds': 40})
            part_train_split = iter(nltk.sent_tokenize(part_train.text))
            for sentence in part_train_split:
                if re.match(".*", sentence) and len(sentence.split()) < 7:
                    question = cleanMessage(sentence)
                    try:
                        answer = cleanMessage(next(part_train_split, None))
                    except AttributeError:
                        print("End of episode" + one_file)
                        continue
                    if len(answer.split()) < 7:
                        # print (sentence, answer)
                        qa_dict[question.strip()] = answer.strip()
    return qa_dict


def cleanMessage(message):
    # Remove new lines within message
    cleanedMessage = message.replace('\n', ' ').lower()
    # Deal with some weird tokens
    cleanedMessage = cleanedMessage.replace("\xc2\xa0", "")
    # Remove punctuation
    cleanedMessage = re.sub('([.,!?-])', '', cleanedMessage)
    # Remove multiple spaces in message
    cleanedMessage = re.sub(' +', ' ', cleanedMessage)
    return cleanedMessage


combinedDictionary = {}
# if (googleData == 'y'):
#     print ('Getting Google Hangout Data')
#     combinedDictionary.update(getGoogleHangoutsData())
# if (fbData == 'y'):
#     print ('Getting Facebook Data')
#     combinedDictionary.update(getFacebookData())
# if (linkedInData == 'y'):
#     print ('Getting LinkedIn Data')
#     combinedDictionary.update(getLinkedInData())
# if (whatsAppData == 'y'):
#         print ('Getting whatsApp Data')
#         combinedDictionary.update(getWhatsAppData())
if (subtitles == 'y'):
    print('Getting whatsubtitles App Data')
    combinedDictionary.update(getSubtitles())

print('Total len of dictionary', len(combinedDictionary))

print('Saving conversation data dictionary')
np.save('conversationDictionary.npy', combinedDictionary)

conversationFile = open('conversationData.txt', 'w')
for key, value in combinedDictionary.items():
    if (not key.strip() or not value.strip()):
        # If there are empty strings
        continue
    try:
        conversationFile.write(key.strip() + " " + value.strip() + " ")
    except:
        print("Encoding problem")
        pass
