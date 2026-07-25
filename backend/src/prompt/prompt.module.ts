import { Module } from '@nestjs/common';
import { PromptController } from './prompt.controller';
import { PromptService } from './prompt.service';
import { RetrievalService } from './retrieval.service';

@Module({
  controllers: [PromptController],
  providers: [PromptService, RetrievalService],
})
export class PromptModule {}
