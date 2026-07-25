import { Injectable } from '@nestjs/common';
import { CreatePromptDto } from './dto/create-prompt.dto';
import { RetrievalService } from './retrieval.service';

const INSTRUCTIONS = `You are answering interview and career questions on behalf of the candidate, \
using only the context below, drawn from their own career documents.

Rules:
- Only use the provided context. Do not use outside knowledge.
- If the context doesn't contain enough to answer, say so plainly instead of guessing.
- Answer in first person, in a natural interview-ready tone.
- If a target company/domain is given, prioritize and frame examples that best match that domain.`;

export interface PromptResult {
  prompt: string;
  sources: { source: string; section: string }[];
}

@Injectable()
export class PromptService {
  constructor(private readonly retrievalService: RetrievalService) {}

  async build(dto: CreatePromptDto): Promise<PromptResult> {
    const chunks = await this.retrievalService.retrieve(
      dto.question,
      dto.companyName,
    );
    const context = chunks.map((chunk) => chunk.text).join('\n\n---\n\n');

    const targetLine = dto.companyName
      ? `Target company: ${dto.companyName}${dto.companyAbout ? ` — ${dto.companyAbout}` : ''}\n\n`
      : '';

    const prompt = `${INSTRUCTIONS}\n\n${targetLine}Context:\n${context}\n\nQuestion: ${dto.question}`;

    return {
      prompt,
      sources: chunks.map((chunk) => ({
        source: chunk.source,
        section: chunk.section,
      })),
    };
  }
}
