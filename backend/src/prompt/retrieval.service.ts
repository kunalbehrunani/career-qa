import { Injectable, InternalServerErrorException } from '@nestjs/common';
import { execFile } from 'child_process';
import { join } from 'path';
import { promisify } from 'util';

const execFileAsync = promisify(execFile);

const PYTHON_DIR = join(
  __dirname,
  '..',
  '..',
  '..',
  'retrieval-augmented-generation',
);
const PYTHON_BIN = join(PYTHON_DIR, 'venv', 'bin', 'python');
const RETRIEVE_SCRIPT = join(PYTHON_DIR, 'retrieve.py');

export interface RetrievedChunk {
  text: string;
  source: string;
  section: string;
}

interface RetrieveOutput {
  chunks?: RetrievedChunk[];
  error?: string;
}

function isRetrieveOutput(value: unknown): value is RetrieveOutput {
  return typeof value === 'object' && value !== null;
}

@Injectable()
export class RetrievalService {
  async retrieve(
    question: string,
    company?: string,
  ): Promise<RetrievedChunk[]> {
    const args = company
      ? [RETRIEVE_SCRIPT, '--company', company, question]
      : [RETRIEVE_SCRIPT, question];

    let stdout: string;
    try {
      const result = await execFileAsync(PYTHON_BIN, args);
      stdout = result.stdout;
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      throw new InternalServerErrorException(
        `Retrieval process failed: ${message}`,
      );
    }

    const parsed: unknown = JSON.parse(stdout);
    if (!isRetrieveOutput(parsed)) {
      throw new InternalServerErrorException(
        'Unexpected output from retrieve.py',
      );
    }

    if (parsed.error) {
      throw new InternalServerErrorException(parsed.error);
    }

    return parsed.chunks ?? [];
  }
}
