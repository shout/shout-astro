import { defineCollection, z } from 'astro:content';

const blog = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    author: z.string().optional(),
    publishDate: z.date(),
    modifiedDate: z.date().optional(),
    image: z.object({
      src: z.string(),
      alt: z.string(),
      width: z.number().optional(),
      height: z.number().optional(),
    }).optional(),
    category: z.string().optional(),
    tags: z.array(z.string()).default([]),
    canonical: z.string().optional(),
    ogImage: z.string().optional(),
    readingTime: z.string().optional(),
  })
});

export const collections = {
  blog,
};