from aiogram import Bot
from typing import List
import asyncio

class Broadcaster:
    def __init__(self, bot: Bot):
        self.bot = bot
    
    async def send_message(self, user_id: int, text: str) -> bool:
        """
        Отправляет сообщение одному пользователю
        
        Args:
            user_id: ID пользователя
            text: Текст сообщения
            
        Returns:
            bool: True если отправка успешна, False если произошла ошибка
        """
        try:
            await self.bot.send_message(user_id, text)
            return True
        except Exception as e:
            print(f"Error sending message to {user_id}: {e}")
            return False
    
    async def broadcast(self, user_ids: List[int], text: str) -> dict:
        """
        Выполняет рассылку сообщения всем пользователям
        
        Args:
            user_ids: Список ID пользователей
            text: Текст сообщения
            
        Returns:
            dict: Статистика рассылки (успешно/неуспешно)
        """
        results = {
            "success": 0,
            "failed": 0
        }
        
        for user_id in user_ids:
            success = await self.send_message(user_id, text)
            if success:
                results["success"] += 1
            else:
                results["failed"] += 1
            
            # Небольшая задержка между отправками
            await asyncio.sleep(0.05)
        
        return results

