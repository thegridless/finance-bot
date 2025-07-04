# -*- coding: utf-8 -*-
"""
Менеджер кеша для категорий
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class CacheManager:
    """Менеджер кеширования категорий"""
    
    def __init__(self, cache_file: str = "categories.json"):
        """
        Инициализация менеджера кеша
        
        Args:
            cache_file (str): Путь к файлу кеша
        """
        self.cache_file = cache_file
        self.cache_expiry_hours = 24  # Кеш истекает через 24 часа
    
    def load_categories(self) -> Dict[str, List[str]]:
        """
        Загрузить категории из кеша
        
        Returns:
            Dict[str, List[str]]: Словарь с категориями {type: [categories]}
        """
        try:
            if not os.path.exists(self.cache_file):
                return {}
            
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Проверяем срок действия кеша
            if self._is_cache_expired(cache_data.get('timestamp')):
                print("📅 Кеш категорий истек")
                return {}
            
            categories = cache_data.get('categories', {})
            print(f"✅ Загружено из кеша: {len(categories)} типов категорий")
            return categories
            
        except Exception as e:
            print(f"❌ Ошибка загрузки кеша: {e}")
            return {}
    
    def save_categories(self, categories: Dict[str, List[str]]) -> bool:
        """
        Сохранить категории в кеш
        
        Args:
            categories (Dict[str, List[str]]): Словарь с категориями
            
        Returns:
            bool: True если успешно сохранено
        """
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'categories': categories
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            total_categories = sum(len(cats) for cats in categories.values())
            print(f"💾 Сохранено в кеш: {total_categories} категорий")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка сохранения кеша: {e}")
            return False
    
    def clear_cache(self) -> bool:
        """
        Очистить кеш
        
        Returns:
            bool: True если успешно очищено
        """
        try:
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
                print("🗑️ Кеш категорий очищен")
            return True
        except Exception as e:
            print(f"❌ Ошибка очистки кеша: {e}")
            return False
    
    def is_cache_valid(self) -> bool:
        """
        Проверить, действителен ли кеш
        
        Returns:
            bool: True если кеш действителен
        """
        try:
            if not os.path.exists(self.cache_file):
                return False
            
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            return not self._is_cache_expired(cache_data.get('timestamp'))
            
        except Exception as e:
            print(f"❌ Ошибка проверки кеша: {e}")
            return False
    
    def get_cache_info(self) -> Dict:
        """
        Получить информацию о кеше
        
        Returns:
            Dict: Информация о кеше
        """
        try:
            if not os.path.exists(self.cache_file):
                return {
                    'exists': False,
                    'message': 'Кеш не найден'
                }
            
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            timestamp = cache_data.get('timestamp')
            categories = cache_data.get('categories', {})
            
            total_categories = sum(len(cats) for cats in categories.values())
            
            if timestamp:
                cache_time = datetime.fromisoformat(timestamp)
                age = datetime.now() - cache_time
                
                return {
                    'exists': True,
                    'timestamp': timestamp,
                    'age_hours': age.total_seconds() / 3600,
                    'total_categories': total_categories,
                    'category_types': list(categories.keys()),
                    'is_expired': self._is_cache_expired(timestamp)
                }
            else:
                return {
                    'exists': True,
                    'message': 'Неверный формат кеша',
                    'total_categories': total_categories
                }
                
        except Exception as e:
            return {
                'exists': False,
                'error': str(e)
            }
    
    def _is_cache_expired(self, timestamp: Optional[str]) -> bool:
        """
        Проверить, истек ли кеш
        
        Args:
            timestamp (Optional[str]): Временная метка в формате ISO
            
        Returns:
            bool: True если кеш истек
        """
        if not timestamp:
            return True
        
        try:
            cache_time = datetime.fromisoformat(timestamp)
            expiry_time = cache_time + timedelta(hours=self.cache_expiry_hours)
            return datetime.now() > expiry_time
        except Exception:
            return True 