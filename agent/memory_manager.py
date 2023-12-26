import numpy as np
import faiss
from typing import List
import logging
import openai
import json
import os
import backoff


class MemoryManager:
    def __init__(self, user_id: str) -> None:
        if not "OPENAI_API_KEY" in os.environ:
            logging.error("❌ 🧠 OPENAI_API_KEY environment variable not set")
            raise Exception("OPENAI_API_KEY environment variable not set")

        self.user_id = user_id
        self.memory = (
            np.load(f"agent/memory/{user_id}.npy")
            if os.path.exists(f"agent/memory/{user_id}.npy")
            else np.zeros((0, 1536))
        )
        self.index = faiss.IndexFlatL2(1536)
        if self.memory.size > 0:
            self.index.add(self.memory)
        if os.path.exists(f"agent/memory/{user_id}.json"):
            with open(f"agent/memory/{user_id}.json", "r", encoding="utf-8") as f:
                self.memory_text = json.load(f)  # List[str]
        else:
            self.memory_text = []
        logging.info(
            f"✅ 🧠 {self.__str__()} Initialized, memory size: {self.index.ntotal}"
        )

    @backoff.on_exception(backoff.constant, Exception, interval=3, max_time=60)
    def embedding(self, text: str, model="text-embedding-ada-002") -> List[float]:
        # length of output: 1536
        response = (
            openai.embeddings.create(
                input=text.replace("\n", ""),
                model=model,
            )
            .data[0]
            .embedding
        )
        return response

    def search(self, query: str, k: int = 3) -> List[str]:
        if self.index.ntotal == 0:
            logging.info(f"✅ 🧠 {self.__str__()} Memory is empty")
            return []
        query_embedding = self.embedding(query)
        if len(query_embedding) == 0:
            logging.warning(f"❌ 🧠 {self.__str__()} Query embedding is empty")
            return []
        _, I = self.index.search(
            np.array([query_embedding]).astype(np.float32),
            k if self.index.ntotal > k else self.index.ntotal,
        )
        logging.info(f"✅ 🧠 {self.__str__()} Search num: {len(I[0])}")
        return [self.memory_text[i] for i in I[0]]

    def add(self, text: str) -> None:
        embed = self.embedding(text)
        if len(embed) == 0:
            logging.warning(f"❌ 🧠 {self.__str__()} Embedding is empty")
            return
        self.memory_text.append(text)
        self.memory = np.append(self.memory, np.array([embed]).astype(np.float32), axis=0)
        self.index.add(np.array([self.memory[-1]]).astype(np.float32))
        self.save()
        logging.info(
            f"✅ 🧠 {self.__str__()} Add memory, memory size: {self.index.ntotal}"
        )

    def delete(self, text: str) -> None:
        index = self.memory_text.index(text)
        self.memory_text.pop(index)
        self.memory = np.delete(self.memory, index, axis=0)
        self.index.remove_ids(np.array([index]))
        self.save()
        logging.info(
            f"✅ 🧠 {self.__str__()} Delete memory, memory size: {self.index.ntotal}"
        )

    def update(self, old_text: str, new_text: str) -> None:
        self.delete(old_text)
        self.add(new_text)
        logging.info(
            f"✅ 🧠 {self.__str__()} Update memory, memory size: {self.index.ntotal}"
        )

    def save(self) -> None:
        with open(f"agent/memory/{self.user_id}.json", "w", encoding="utf-8") as f:
            json.dump(self.memory_text, f, ensure_ascii=False)
        np.save(f"agent/memory/{self.user_id}.npy", self.memory)

    def __str__(self) -> str:
        return f"MemoryManager for {self.user_id}"


if __name__ == "__main__":
    memory_manager = MemoryManager("@1213hahahasdasdahaha")
    # memory_manager.update("[moderately]User prefers a soft reminder", "haaaaaaaahaah")
    print(memory_manager.search("haha"))