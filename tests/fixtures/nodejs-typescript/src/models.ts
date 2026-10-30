export interface Item {
  id: string;
  title: string;
  description: string;
  price: number;
  createdAt: Date;
}

export interface CreateItemDto {
  title: string;
  description: string;
  price: number;
}
