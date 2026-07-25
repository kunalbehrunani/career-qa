import { Body, Controller, Post } from '@nestjs/common';
import { CreatePromptDto } from './dto/create-prompt.dto';
import { PromptResult, PromptService } from './prompt.service';

@Controller('prompt')
export class PromptController {
  constructor(private readonly promptService: PromptService) {}

  @Post()
  create(@Body() dto: CreatePromptDto): Promise<PromptResult> {
    return this.promptService.build(dto);
  }
}
