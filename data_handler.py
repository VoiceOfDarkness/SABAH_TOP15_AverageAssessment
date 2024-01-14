class DataHandler:
    def __init__(self, collection):
        self.collection = collection

    async def add_data(
        self, student_id, subjects_credits, student_ratings, student_name
    ):
        self.collection.find_one_and_update(
            {"_id": student_id},
            {
                "$set": {
                    "subjects_credits": subjects_credits,
                    "ratings": student_ratings,
                    "name": student_name,
                }
            },
            upsert=True,
        )

    async def delete_student_data(self, student_id):
        self.collection.find_one_and_delete({"_id": student_id})

    async def calculate(self, message, state):
        cursor_credits = self.collection.find({}, {"subjects_credits": 1})
        cursor_ratings = self.collection.find({}, {"ratings": 1})
        cursor_names = self.collection.find({}, {"name": 1})
        for doc in cursor_credits:
            means_kredit = doc["subjects_credits"]
        ratings = [doc["ratings"] for doc in cursor_ratings]
        names = {i + 1: doc["name"] for i, doc in enumerate(cursor_names)}

        if means_kredit and ratings:
            lst = []
            result = [
                [rating[i] * means_kredit[i] for i in range(len(rating))]
                for rating in ratings
            ]

            data_names = dict(zip(names.values(), ratings))

            for name in names.values():
                grade = data_names[name]
                if all(num >= 91 for num in grade):
                    lst.append(name)

            sorted_ratings = [(names[i + 1], result[i]) for i in range(len(result))]
            sorted_ratings.sort(key=lambda x: sum(x[1]), reverse=True)

            response = ""
            for i, (name, ratings) in enumerate(sorted_ratings):
                if name in lst:
                    response += f"{i+1}. {name}: {round(sum(ratings) / sum(means_kredit), 3)}, A\n"
                else:
                    response += (
                        f"{i+1}. {name}: {round(sum(ratings) / sum(means_kredit), 3)}\n"
                    )

            await message.answer(response)
        else:
            await message.reply(
                "Lütfən, vasitələrin_krediti, reytinqlər və adlar üçün dəyərlər təyin edin."
            )
