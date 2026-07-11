import { mockDelay } from "./mock-delay";
import { notFound } from "./errors";

export async function mockResponse<T>(data: T): Promise<T> {
  await mockDelay();
  return data;
}

export async function mockFindResponse<T>(items: T[], predicate: (item: T) => boolean, resource: string, id: string): Promise<T> {
  await mockDelay();
  return findMockOrThrow(items, predicate, resource, id);
}

export function findMockOrThrow<T>(items: T[], predicate: (item: T) => boolean, resource: string, id: string): T {
  const item = items.find(predicate);
  if (!item) throw notFound(resource, id);
  return item;
}
