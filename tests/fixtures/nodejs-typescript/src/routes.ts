import { Router, Request, Response } from 'express';
import { Item, CreateItemDto } from './models';

export const router = Router();

const items: Item[] = [
  {
    id: 'item-1',
    title: 'Keyboard',
    description: 'Mechanical gaming keyboard',
    price: 99.99,
    createdAt: new Date(),
  },
];

router.get('/health', (req: Request, res: Response) => {
  res.json({ status: 'ok', uptime: process.uptime() });
});

router.get('/items', (req: Request, res: Response) => {
  res.json({ data: items, count: items.length });
});

router.post('/items', (req: Request, res: Response) => {
  const body = req.body as CreateItemDto;
  const newItem: Item = {
    id: `item-${items.length + 1}`,
    title: body.title,
    description: body.description,
    price: body.price,
    createdAt: new Date(),
  };
  items.push(newItem);
  res.status(201).json(newItem);
});
