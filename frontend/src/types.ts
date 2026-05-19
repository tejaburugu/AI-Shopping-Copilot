export interface Product {
  id: string;
  title: string;
  brand: string;
  category: string;
  price: number;
  rating: number;
  description: string;
  reviews: string[];
  image_url: string;
}

export interface AskResponse {
  query: string;
  answer: string;
  contextual_query?: string;
  previous_queries?: string[];
  products: Product[];
}
