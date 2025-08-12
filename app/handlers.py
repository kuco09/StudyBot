import random as r

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import app.dataBase as db
import app.states as s

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await message.answer("Hello. I'm a bot to study words from other languages. You write your words and can remember them. So good studying!")
    await message.answer("Choose language", reply_markup=kb.mainMenu)

@router.message(F.text == "🔙 Back to menu")
async def backTomenu(message: Message, state: FSMContext):
    await goBack(message, state)

@router.message(F.text == "✍️ Write new words")
async def writeNew(message: Message):
    await message.answer("What do you want to do?", reply_markup=kb.groupOperation)

@router.message(F.text == "🗂️ Make new group")
async def makeGroup(message: Message, state:FSMContext):
    await state.set_state(s.Write.group)
    await message.answer("Write name to group", reply_markup=kb.backButton)

@router.message(s.Write.group)
async def WriteWord(message: Message, state: FSMContext):
    if message.text != "🔙 Back to menu":
        if message.text in db.getListOfGroups(message.from_user.id):
            await state.set_state(s.Write.group)
            await message.answer("This group already exists")
        else:
            await state.update_data(group=message.text)
            await state.set_state(s.Write.word)
            await message.answer("Now write your words like this: \n<talk-sprechen>")
    else:
        await goBack(message, state)

@router.message(s.Write.word)
async def writeFirstLan(message: Message, state: FSMContext):
    if message.text != "🔙 Back to menu":
        await state.update_data(word=message.text)
        data = await state.get_data()
        await state.update_data(word=None)

        words = data["word"].split("-")
        if len(words) == 2 and message.text not in db.getListOfWords(data["group"], message.from_user.id):
            db.addWordToDataBase(words, message.from_user.id, data["group"])
            await state.set_state(s.Write.word)
            await message.answer("Write next word or end")
        else:
            await state.set_state(s.Write.word)
            await message.answer("Word is incorrect or already exists! Please try again.")
    else:
        await goBack(message, state)

@router.message(F.text == "✏️ Change exist group")
async def changeGroup(message: Message, state: FSMContext):
    text = ""
    for index, ele in enumerate(db.getListOfGroups(message.from_user.id), start=1):
        text += f"{index}. {ele}\n"
    await state.set_state(s.ChooseGroup.num)
    await message.answer(f"List of groups:\n{text}")
    await message.answer("Write number of group you want to change:", reply_markup=kb.backButton)

@router.message(s.ChooseGroup.num)
async def chooseChangesForGroup(message: Message, state: FSMContext):
    if message.text != "🔙 Back to menu":
        await state.update_data(num=message.text)
        data = await state.get_data()

        if data["num"].isdigit() and int(data["num"]) <= len(db.getListOfGroups(message.from_user.id)):
            group = db.getListOfGroups(message.from_user.id)[int(data["num"]) - 1]
            await state.update_data(group=group)
            if not group:
                await message.answer("Error!\nPlease try again.", reply_markup=kb.mainMenu)
                return

            await message.answer(f"You chose: {group}\nWhat do you want to do?", reply_markup=kb.changeGroup)
        else:
            await state.set_state(s.ChooseGroup.num)
            await message.answer("Incorrect number\nPlease try again.")
    else:
        await goBack(message, state)

@router.callback_query(F.data == "delete_word")
async def changeWordsFromGroup(callback: CallbackQuery, state: FSMContext):
    await callback.answer("")
    await callback.message.delete()

    data = await state.get_data()
    group = data.get("group")

    text = ""
    for index, ele in enumerate(db.getListOfWords(group, callback.from_user.id, True), start=1):
        text += f"{index}. {ele}\n"
    await state.set_state(s.ChooseWord.num)
    await callback.message.answer(f"Choose word:\n{text}")

@router.message(s.ChooseWord.num)
async def chooseWordFromGroup(message: Message, state: FSMContext):
    if message.text != "🔙 Back to menu":
        await state.update_data(num=message.text)
        data = await state.get_data()
        group = data.get("group")
        if not group:
            await message.answer("Error!\nPlease try again.", reply_markup=kb.mainMenu)
            return

        if data["num"].isdigit() and int(data["num"]) <= len(db.getListOfWords(group, message.from_user.id, True)):
            word = db.getListOfWords(group, message.from_user.id, True)[int(data["num"]) - 1]
            db.deleteWord(group, message.from_user.id, word)
            await message.answer("Word was deleted", reply_markup=kb.mainMenu)
            await state.clear()
        else:
            await state.set_state(s.ChooseWord.num)
            await message.answer("Incorrect number\nPlease try again.")
    else:
        await goBack(message, state)

@router.callback_query(F.data == "delete_group")
async def deleteGroup(callback: CallbackQuery, state: FSMContext):
    await callback.answer("")

    isNew = False
    data = await state.get_data()
    group = data.get("group")

    if not group:
        await callback.message.answer("Error!\nPlease try again.", reply_markup=kb.mainMenu)
        return
    
    if db.isGroupNew(group, callback.from_user.id):
        isNew = True

    db.deleteGroup(group, callback.from_user.id)
    if isNew:
        list = db.getListOfGroups(callback.from_user.id)
        db.makeGroupNew(list[-1], callback.from_user.id)

    await callback.message.answer("Group is deleted", reply_markup=kb.mainMenu)
    await state.clear()

@router.message(F.text == "📚 Study new words")
async def studyNewWords(message: Message, state: FSMContext):
    listOfNew = db.getListWordsByStatus(message.from_user.id, "new")

    if listOfNew == []:
        await message.answer("You don`t have new words!!!", reply_markup=kb.mainMenu)
        return
    
    r.shuffle(listOfNew)

    await state.update_data(list=listOfNew)
    await state.update_data(index=0)
    await state.update_data(correct=0)
    await state.update_data(lenWords= len(listOfNew))
    await state.set_state(s.TestNew.word)

    await message.answer(listOfNew[0][0], reply_markup=kb.backButton)

@router.message(s.TestNew.word)
async def testNewWords(message: Message, state: FSMContext):
    if message.text != "🔙 Back to menu":
        await state.update_data(word=message.text)
        data = await state.get_data()
        index = data.get("index")
        list = data.get("list")
        correct = data.get("correct")

        if data["word"].lower() == list[index][1]:
            await message.answer("Correct! ✅")
            correct += 1
            await state.update_data(correct=correct)
        else:
            await message.answer(f"Incorrect! ❌\n{list[index][1]}")
        index += 1
        await state.update_data(index=index)

        if index == len(list):
            await repeatOldWords(message, state)
            return

        await state.set_state(s.TestNew.word)
        await message.answer(list[index][0])
    else:
        await goBack(message, state)

async def repeatOldWords(message: Message, state: FSMContext):
    listOfOld = db.getListWordsByStatus(message.from_user.id, "old")
    r.shuffle(listOfOld)

    await state.update_data(list=listOfOld)
    await state.update_data(index=0)
    data = await state.get_data()
    lenWords = data.get("lenWords")
    lenWords += 5
    await state.update_data(lenWords=lenWords)

    await state.set_state(s.RepeatOld.word)
    await message.answer(listOfOld[0][0])

@router.message(s.RepeatOld.word)
async def testOldWords(message: Message, state: FSMContext):
    if message.text != "🔙 Back to menu":
        await state.update_data(word= message.text)
        data = await state.get_data()
        index = data.get("index")
        list = data.get("list")
        correct = data.get("correct")

        if data["word"].lower() == list[index][1]:
            await message.answer("Correct! ✅")
            correct += 1
            await state.update_data(correct=correct)
        else:
            await message.answer(f"Incorrect! ❌\n{list[index][1]}")
        index += 1
        await state.update_data(index=index)

        if index == db.getNOROW(message.from_user.id):
            lenWords = data.get("lenWords")
            await message.answer(f"Score: {correct}/{lenWords}", reply_markup=kb.mainMenu)
            await state.clear()
            return

        await state.set_state(s.RepeatOld.word)
        await message.answer(list[index][0])
    else:
        await goBack(message, state)


# Study old words
@router.message(F.text == "📂 Study exact group")
async def studyOldGroup(message: Message, state: FSMContext):
    text = ""
    for index, ele in enumerate(db.getListOfGroups(message.from_user.id), start=1):
        text += f"{index}. {ele}\n"
    await state.set_state(s.ChooseOldGroup.num)
    await message.answer(f"Choose Group:\n{text}")
    await message.answer("Write number of group you want to study:", reply_markup=kb.backButton)

@router.message(s.ChooseOldGroup.num)
async def chooseOldGroup(message: Message, state: FSMContext):
    if message.text != "🔙 Back to menu":
        await state.update_data(num=message.text)
        data = await state.get_data()

        if data["num"].isdigit() and int(data["num"]) <= len(db.getListOfGroups(message.from_user.id)):
            group = db.getListOfGroups(message.from_user.id)[int(data["num"]) - 1]
            if not group:
                await message.answer("Error!\nPlease try again.", reply_markup=kb.mainMenu)
                return
            await state.clear()
            await startStudyOldGroup(message, state, group)
            return
        else:
            await state.set_state(s.ChooseGroup.num)
            await message.answer("Incorrect number\nPlease try again.")
    else:
        await goBack(message, state)


async def startStudyOldGroup(message: Message, state: FSMContext, group):
    listOfOld = db.getListOfWords(group, message.from_user.id, split=True)
    r.shuffle(listOfOld)

    await state.update_data(list=listOfOld)
    await state.update_data(index=0)
    await state.update_data(correct=0)
    await state.update_data(lenWords= len(listOfOld))
    await state.set_state(s.StudyOldWord.word)

    await message.answer(listOfOld[0][0], reply_markup=kb.backButton)

@router.message(s.StudyOldWord.word)
async def studyOldGroup(message: Message,state: FSMContext):
    if message.text != "🔙 Back to menu":
        await state.update_data(word=message.text)
        data = await state.get_data()
        index = data.get("index")
        list = data.get("list")
        correct = data.get("correct")

        if data["word"].lower() == list[index][1]:
            await message.answer("Correct! ✅")
            correct += 1
            await state.update_data(correct=correct)
        else:
            await message.answer(f"Incorrect! ❌\n{list[index][1]}")
        index += 1
        await state.update_data(index=index)
        
        if index == len(list):
            lenWords = data.get("lenWords")
            await message.answer(f"Score: {correct}/{lenWords}", reply_markup=kb.mainMenu)
            await state.clear()
            return    
        
        await state.set_state(s.StudyOldWord.word)
        await message.answer(list[index][0])
    else:
        await goBack(message, state)


# Settings

@router.message(F.text == "⚙️ Settings")
async def chooseSettings(message: Message):
    numRepeatOldWords = db.getNOROW(message.from_user.id)
    if numRepeatOldWords == 5:
        await message.answer("--⚙️Settings⚙️--\n number of repeat old words: 5 (default)", reply_markup=kb.changeSettings)
    else:
        await message.answer(f"--⚙️Settings⚙️--\n number of repeat old words: {numRepeatOldWords}", reply_markup=kb.changeSettings)

@router.callback_query(F.data == "num_of_repeat_old_words")
async def changeNOROW(callback: CallbackQuery, state: FSMContext):
    await state.set_state(s.ChangeNOROW.num)
    await callback.answer("")
    await callback.message.answer(f"Write number (min: 1, max: {len(db.getListWordsByStatus(callback.from_user.id, "old"))}):", reply_markup=kb.backButton)

@router.message(s.ChangeNOROW.num)
async def changeNOROW2(message: Message, state: FSMContext):
    if message.text != "🔙 Back to menu":
        await state.update_data(num=message.text)
        data = await state.get_data()

        if data["num"].isdigit() and int(data["num"]) <= len(db.getListWordsByStatus(message.from_user.id, "old")) and int(data["num"]) >= 1:
            db.setNOROW(message.from_user.id, data["num"])
            await goBack(message, state)
        else:
            await state.set_state(s.ChangeNOROW.num)
            await message.answer("Something went wrong\n please try again:")
    else:
        await goBack(message, state)

async def goBack(message: Message, state: FSMContext):
    await message.answer("Save and back", reply_markup=kb.mainMenu)
    await state.clear()