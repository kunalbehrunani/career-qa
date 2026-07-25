<script setup lang="ts">
import { ref } from 'vue';
import { fetchPrompt, type PromptSource } from './services/promptApi';

const companyName = ref('');
const companyAbout = ref('');
const question = ref('');

const prompt = ref('');
const sources = ref<PromptSource[]>([]);
const loading = ref(false);
const error = ref('');
const copied = ref(false);

async function onSubmit() {
  error.value = '';
  copied.value = false;
  loading.value = true;
  try {
    const result = await fetchPrompt({
      question: question.value,
      companyName: companyName.value || undefined,
      companyAbout: companyAbout.value || undefined,
    });
    prompt.value = result.prompt;
    sources.value = result.sources;
  } catch (err: unknown) {
    error.value = err instanceof Error ? err.message : 'Something went wrong.';
  } finally {
    loading.value = false;
  }
}

function onReset() {
  companyName.value = '';
  companyAbout.value = '';
  question.value = '';
  prompt.value = '';
  sources.value = [];
  error.value = '';
  copied.value = false;
}

async function copyPrompt() {
  await navigator.clipboard.writeText(prompt.value);
  copied.value = true;
  setTimeout(() => (copied.value = false), 2000);
}
</script>

<template>
  <div class="flex h-screen flex-col bg-gray-50 text-gray-900 md:flex-row">
    <!-- Left panel: input -->
    <section class="overflow-y-auto border-b border-gray-200 p-8 md:w-1/2 md:border-b-0 md:border-r">
      <div class="mx-auto max-w-lg">
        <h1 class="text-3xl font-medium text-gray-900">CareerQA</h1>
        <p class="mt-1 text-gray-500">
          Answers interview questions, tailored to the company you're targeting.
        </p>

        <form class="mt-8 space-y-5" @submit.prevent="onSubmit">
          <div>
            <label class="mb-1 block text-sm font-medium text-gray-700">Company name</label>
            <input
              v-model="companyName"
              type="text"
              placeholder="e.g. Visa"
              class="w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label class="mb-1 block text-sm font-medium text-gray-700">
              Company about <span class="font-normal text-gray-400">(optional)</span>
            </label>
            <textarea
              v-model="companyAbout"
              rows="2"
              placeholder="e.g. Global payments company"
              class="w-full resize-y rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            ></textarea>
          </div>

          <div>
            <label class="mb-1 block text-sm font-medium text-gray-700">Question</label>
            <textarea
              v-model="question"
              rows="5"
              required
              placeholder="e.g. Tell me about your best project"
              class="w-full resize-y rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            ></textarea>
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full rounded-full bg-blue-600 px-6 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-blue-700 hover:shadow-md disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:shadow-sm"
          >
            {{ loading ? 'Generating…' : 'Generate prompt' }}
          </button>
        </form>

        <p v-if="error" class="mt-4 text-sm text-red-600">{{ error }}</p>
      </div>
    </section>

    <!-- Right panel: output -->
    <section class="flex overflow-y-auto p-8 md:w-1/2">
      <div class="mx-auto flex w-full max-w-lg flex-1 flex-col">
        <div class="mb-4 flex items-center justify-between">
          <h2 class="text-lg font-medium text-gray-900">Generated prompt</h2>
          <div class="flex gap-2">
            <button
              type="button"
              class="rounded-full border border-gray-300 bg-white px-4 py-1.5 text-sm font-medium text-gray-700 shadow-sm transition hover:bg-gray-50"
              @click="onReset"
            >
              Reset
            </button>
            <button
              type="button"
              :disabled="!prompt"
              class="rounded-full bg-blue-600 px-4 py-1.5 text-sm font-medium text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
              @click="copyPrompt"
            >
              {{ copied ? 'Copied!' : 'Copy' }}
            </button>
          </div>
        </div>

        <pre
          v-if="prompt"
          class="flex-1 overflow-y-auto whitespace-pre-wrap rounded-xl border border-gray-200 bg-white p-4 text-sm text-gray-800 shadow-sm"
          >{{ prompt }}</pre
        >
        <p v-else class="text-sm italic text-gray-400">Your generated prompt will appear here.</p>

        <details v-if="sources.length" class="mt-4 text-sm text-gray-500">
          <summary class="cursor-pointer font-medium">Sources ({{ sources.length }})</summary>
          <ul class="mt-2 list-inside list-disc space-y-1">
            <li v-for="(s, i) in sources" :key="i">{{ s.source }} / {{ s.section }}</li>
          </ul>
        </details>
      </div>
    </section>
  </div>
</template>
