import sqlite3

if __name__ == "__main__":
    db = sqlite3.connect("user_settings.db")
    c = db.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS user_settings(
        user_id INTEGER,
        repeatOldWords INTEGER
    )""")

def addWordToDataBase(words, user_id, group):
    db = sqlite3.connect("app/words.db")
    c = db.cursor()

    words[0].strip()
    words[1].strip()

    if group in getListOfGroups(user_id) and isGroupNew(group, user_id):
        c.execute("INSERT INTO words VALUES (?, ?, ?, ?, ?)",
            (user_id, words[0].lower(), words[1].lower(), group.lower(), "new"))

    elif group in getListOfGroups(user_id) and not isGroupNew(group, user_id):
        c.execute("INSERT INTO words VALUES (?, ?, ?, ?, ?)",
            (user_id, words[0].lower(), words[1].lower(), group.lower(), "old"))
    else:
        updateNewGroup(user_id)
        c.execute("INSERT INTO words VALUES (?, ?, ?, ?, ?)",
            (user_id, words[0].lower(), words[1].lower(), group.lower(), "new"))

    db.commit()
    db.close()

def isGroupNew(group, user_id):
    db = sqlite3.connect("app/words.db")
    c = db.cursor()

    c.execute("SELECT EXISTS(SELECT 1 FROM words WHERE status = ? AND wordGroup = ? AND user_id = ?)", ("new", group, user_id))
    return c.fetchone()[0]

def amountOfNewWord():
    db = sqlite3.connect("app/words.db")
    c = db.cursor()

    num = c.execute("SELECT COUNT(*) FROM words WHERE status = 'new'")
    db.close()
    return num

def getListWordsByStatus(user_id, status):
    db = sqlite3.connect("app/words.db")
    c = db.cursor()

    c.execute("SELECT firstLan, secondLan FROM words WHERE user_id = ? AND status = ?", (user_id, status))
    result = c.fetchall()

    db.close()
    return result



def getListOfGroups(user_id):
    db = sqlite3.connect("app/words.db")
    c = db.cursor()

    c.execute("SELECT DISTINCT wordGroup FROM words WHERE user_id = ?", (user_id,))
    result = c.fetchall()
    groups = [group[0] for group in result]

    db.close()
    return groups


def getListOfWords(group, user_id, discinct=False, split=False):
    db = sqlite3.connect("app/words.db")
    c = db.cursor()

    if discinct:
        c.execute("SELECT DISTINCT firstLan, secondLan FROM words WHERE wordGroup = ? AND user_id = ?", (group, user_id))
    else:
        c.execute("SELECT firstLan, secondLan FROM words WHERE wordGroup = ? AND user_id = ?", (group, user_id))

    result = c.fetchall()

    if not split:
        wordsList = []
        for ele in result:
            wordsList.append(f"{ele[0]} - {ele[1]}")
            db.close()
            return wordsList
    
    db.close()
    return result

def deleteWord(group, user_id, word):
    db = sqlite3.connect("app/words.db")
    c = db.cursor()

    word = word.split(" - ")
    c.execute("DELETE FROM words WHERE wordGroup = ? AND user_id = ? AND firstLan = ? AND secondLan = ?", (group, user_id, word[0], word[1]))
    
    db.commit()
    db.close()

def deleteGroup(group, user_id):
    db = sqlite3.connect("app/words.db")
    c = db.cursor()

    c.execute("DELETE FROM words WHERE wordGroup = ? AND user_id = ?", (group, user_id))

    db.commit()
    db.close()

def updateNewGroup(user_id):
    db = sqlite3.connect("app/words.db")
    c = db.cursor()

    c.execute("UPDATE words SET status = 'old' WHERE status = 'new' AND user_id = ?", (user_id, ))
    db.commit()
    db.close()

def makeGroupNew(group, user_id):
    db = sqlite3.connect("app/words.db")
    c = db.cursor()

    c.execute("UPDATE words SET status = 'new' WHERE user_id = ? AND wordGroup = ? AND status = 'old'", (user_id, group))
    db.commit()
    db.close()


def getNOROW(user_id):
    db = sqlite3.connect("app/user_settings.db")
    c = db.cursor()

    c.execute("SELECT repeatOldWords FROM user_settings WHERE user_id = ?", (user_id,))
    result = c.fetchone()

    if result:
        value = result[0]
    else:
        value = 5

    db.close()
    return value

def setNOROW(user_id, value):
    db = sqlite3.connect("app/user_settings.db")
    c = db.cursor()

    c.execute("INSERT INTO user_settings VALUES (?, ?)", (user_id, value))
    db.commit()
    db.close()

#7215209827