# <p align="center">Бот помощник по битвам в PoD

<p align="center">if u can

В проекте используется [MongoDB](https://docs.mongodb.com/), [драйвер](https://github.com/ZeoAlliance/aiomongo)<br>
Для ваших основных функций, на которые регистрируются хендлеры будут применены паттерны DI, зависимости могут быть 2 типов:
  * User - Документ пользователя из бд, (ponytypes.UserType)
  * Chat - Документ чата из бд, (ponytypes.ChatType)

```python
from aiogram import types
from support import ponytypes

async def funcname(message: types.Message, User: ponytypes.UserType):
    output = f"Здарова, {User.name}, выглядишь не очень\n"
    await message.answer(output)

async def funcname(call: types.CallbackQuery, User: ponytypes.UserType):
    output = "Твоя сила была обновлена!"
    User.power += 100
    await User.save()
    await call.answer(output, show_alert=True)

async def funcname(message: types.Message, Chat: ponytypes.ChatType):
    Chat.order = "Чат геев"
    await Chat.save()
    await message.answer(Chat.order)
```