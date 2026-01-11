"""
Embeddings generation using Azure OpenAI
"""
from typing import List
from openai import AzureOpenAI
from app.config import settings
import time


class EmbeddingsGenerator:
    """Generate embeddings using Azure OpenAI"""
    
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint
        )
        self.deployment = settings.azure_openai_embedding_deployment
        self.cache = {}  # Simple in-memory cache
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        # Check cache
        if text in self.cache:
            return self.cache[text]
        
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.deployment
            )
            embedding = response.data[0].embedding
            
            # Cache the result
            self.cache[text] = embedding
            
            return embedding
        except Exception as e:
            raise Exception(f"Error generating embedding: {str(e)}")
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 16) -> List[List[float]]:
        """Generate embeddings for multiple texts in batches"""
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            try:
                response = self.client.embeddings.create(
                    input=batch,
                    model=self.deployment
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
                
                # Rate limiting - small delay between batches
                if i + batch_size < len(texts):
                    time.sleep(0.1)
                    
            except Exception as e:
                print(f"Error in batch {i}-{i+batch_size}: {str(e)}")
                # Fallback to individual processing for this batch
                for text in batch:
                    try:
                        emb = self.generate_embedding(text)
                        embeddings.append(emb)
                    except Exception as e2:
                        print(f"Error generating embedding: {str(e2)}")
                        # Use zero vector as fallback
                        embeddings.append([0.0] * 1536)
        
        return embeddings
