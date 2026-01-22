<template>
  <div class="min-h-96">
    <div class="flex flex-col gap-5">
      <div>
        <div 
          class="text-xl font-semibold mb-2"
          :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
        >
          Select or Create Reporter
        </div>
        <p 
          class="text-sm mb-5"
          :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
        >
          Search for an existing reporter or create a new one. Only the reporter's name is required.
        </p>

        <!-- Search Section -->
        <div class="mb-5">
          <div class="flex gap-3 items-center mb-4">
            <div 
              class="relative flex items-center gap-2 border rounded-lg px-3 py-2.5 flex-1 max-w-xs focus-within:ring-2 transition-all"
              :class="isDarkMode 
                ? 'border-transparent bg-neutral-800 focus-within:border-amber-600 focus-within:ring-amber-500/50' 
                : 'border-transparent bg-gray-50 focus-within:border-amber-600 focus-within:ring-amber-600/50'"
            >
              <i-mdi-magnify 
                class="w-5 h-5"
                :class="isDarkMode ? 'text-gray-400' : 'text-gray-500'"
              />
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search by name or phone..."
                class="border-0 outline-none w-full text-sm bg-transparent placeholder-gray-500"
                :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
                @input="handleSearchInput"
              />
            </div>
            <button
              type="button"
              class="h-10 px-4 text-white rounded-lg text-sm font-medium transition-all flex items-center gap-2 whitespace-nowrap"
              :class="isDarkMode 
                ? 'bg-amber-600 hover:bg-amber-700' 
                : 'bg-amber-700 hover:bg-amber-800'"
              @click="openCreateReporterForm"
            >
              <i-mdi-plus class="w-5 h-5" />
              New Reporter
            </button>
          </div>
        </div>

        <!-- Loading State -->
        <div 
          v-if="isLoading" 
          class="flex items-center gap-3 p-5 text-center"
          :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
        >
          <div 
            class="w-5 h-5 border-2 rounded-full animate-spin"
            :class="isDarkMode 
              ? 'border-transparent border-t-amber-500' 
              : 'border-transparent border-t-amber-600'"
          ></div>
          <span>Searching reporters...</span>
        </div>

        <!-- Search Results -->
        <div class="flex flex-col gap-2 max-h-96 overflow-y-auto" v-else-if="shouldShowResults && filteredContacts.length">
          <div 
            class="py-2 text-sm border-b mb-3"
            :class="isDarkMode 
              ? 'text-gray-400 border-transparent' 
              : 'text-gray-600 border-transparent'"
          >
            <span>{{ filteredContacts.length }} reporter(s) found</span>
          </div>
          <div
            v-for="contact in filteredContacts"
            :key="getContactId(contact)"
            class="flex items-center gap-3 border rounded-lg p-3 cursor-pointer transition-all"
            :class="isSelected(contact)
              ? isDarkMode 
                ? 'border-amber-600 bg-amber-900/20' 
                : 'border-amber-600 bg-amber-100'
              : isDarkMode
                ? 'border-transparent bg-neutral-900 hover:bg-neutral-800 hover:border-amber-600'
                : 'border-transparent bg-white hover:bg-gray-50 hover:border-amber-600'"
            @click="selectExistingReporter(contact)"
          >
            <div 
              class="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold text-sm flex-shrink-0"
              :class="isDarkMode ? 'bg-amber-600' : 'bg-amber-700'"
            >
              <span>{{ getInitials(getValue(contact, 'fullname') || 'NA') }}</span>
            </div>

            <div class="flex-1 min-w-0">
              <div class="flex flex-col gap-2">
                <div class="flex flex-col gap-1">
                  <div 
                    class="font-semibold text-base leading-tight truncate"
                    :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
                  >
                    {{ getValue(contact, 'fullname') || "Unnamed Reporter" }}
                  </div>
                  <div 
                    class="text-sm leading-tight"
                    :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
                  >
                    {{ getValue(contact, 'phone') || 'No phone' }}
                  </div>
                </div>
                <div class="flex items-center gap-2 mt-1">
                  <div class="flex gap-2 flex-wrap">
                    <span 
                      v-if="getValue(contact, 'age')" 
                      class="border rounded-full px-2.5 py-1 text-xs font-medium whitespace-nowrap"
                      :class="isDarkMode 
                        ? 'border-transparent bg-neutral-800 text-gray-300' 
                        : 'border-transparent bg-gray-100 text-gray-700'"
                    >
                      {{ getValue(contact, 'age') }}y
                    </span>
                    <span 
                      v-if="getValue(contact, 'sex')" 
                      class="border rounded-full px-2.5 py-1 text-xs font-medium whitespace-nowrap"
                      :class="isDarkMode 
                        ? 'border-transparent bg-neutral-800 text-gray-300' 
                        : 'border-transparent bg-gray-100 text-gray-700'"
                    >
                      {{ getValue(contact, 'sex') }}
                    </span>
                    <span 
                      v-if="getValue(contact, 'location')" 
                      class="border rounded-full px-2.5 py-1 text-xs font-medium whitespace-nowrap flex items-center gap-1 transition-colors"
                      :class="isDarkMode 
                        ? 'bg-amber-500/10 text-amber-500 border-amber-500/20' 
                        : 'bg-amber-600/10 text-amber-600 border-amber-600/20'"
                    >
                      <i-mdi-map-marker class="w-3 h-3" />
                      {{ getValue(contact, 'location') }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div class="flex-shrink-0">
              <i-mdi-check-circle 
                v-if="isSelected(contact)" 
                class="w-5 h-5"
                :class="isDarkMode ? 'text-amber-500' : 'text-amber-600'"
              />
              <i-mdi-chevron-right 
                v-else 
                class="w-5 h-5 text-gray-500"
              />
            </div>
          </div>
        </div>

        <!-- No Results -->
        <div 
          v-else-if="shouldShowResults && !filteredContacts.length" 
          class="text-center p-10 rounded-lg border"
          :class="isDarkMode 
            ? 'text-gray-400 bg-neutral-900 border-transparent' 
            : 'text-gray-500 bg-white border-transparent'"
        >
          <i-mdi-account-search class="mx-auto text-5xl mb-3 opacity-50" />
          <div class="text-base font-medium mb-1">No reporters found</div>
          <div class="text-sm opacity-70">Try searching with a different name or phone number</div>
        </div>

        <!-- Search Prompt -->
        <div 
          v-else-if="!searchQuery.trim() && !showCreateForm" 
          class="text-center p-10 rounded-lg border"
          :class="isDarkMode 
            ? 'text-gray-400 bg-neutral-900 border-transparent' 
            : 'text-gray-500 bg-white border-transparent'"
        >
          <i-mdi-account-group class="mx-auto text-5xl mb-3 opacity-50" />
          <div class="text-base font-medium mb-1">Start typing to search for existing reporters</div>
          <div class="text-sm opacity-70">Or click "New Reporter" to create a new one</div>
        </div>

        <!-- Combined Selected Reporter Summary & ID Display -->
        <div 
          v-if="(selectedReporter || (extractedReporterId && extractedContactId)) && !showCreateForm" 
          class="mt-5 p-4 border rounded-lg"
          :class="isDarkMode 
            ? 'bg-amber-900/20 border-amber-600/30' 
            : 'bg-amber-50 border-amber-300'"
        >
          <div class="flex items-start justify-between mb-3">
            <div 
              class="text-sm font-bold uppercase tracking-tight transition-colors"
              :class="isDarkMode ? 'text-amber-500' : 'text-amber-600'"
            >
              Selected Reporter:
            </div>
            <button 
              type="button" 
              @click="clearSelection" 
              class="p-1.5 rounded-md border transition-colors"
              :class="isDarkMode 
                ? 'border-transparent hover:bg-neutral-800 hover:border-red-500 text-gray-400 hover:text-red-400' 
                : 'border-transparent hover:bg-gray-100 hover:border-red-500 text-gray-600 hover:text-red-600'"
            >
              <i-mdi-close class="w-4 h-4" />
            </button>
          </div>
          
          <div class="flex items-start gap-3">
            <div 
              class="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold text-sm flex-shrink-0"
              :class="isDarkMode ? 'bg-amber-600' : 'bg-amber-700'"
            >
              <span>{{ getInitials(getValue(selectedReporter, 'fullname') || 'NR') }}</span>
            </div>
            
            <div class="flex-1 min-w-0">
              <div 
                class="font-semibold text-base mb-1"
                :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
              >
                {{ getValue(selectedReporter, 'fullname') || 'Reporter' }}
              </div>
              
              <div 
                class="text-sm space-y-1 mb-3"
                :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
              >
                <div>{{ getValue(selectedReporter, 'phone') || 'No phone' }}</div>
                <div>
                  {{ getValue(selectedReporter, 'age') || 'Age unknown' }} • 
                  {{ getValue(selectedReporter, 'sex') || 'Gender unknown' }}
                </div>
              </div>

              <!-- Reporter IDs Display -->
              <div class="space-y-2">
                <div 
                  v-if="extractedReporterId" 
                  class="flex items-center gap-2 p-2 border rounded-md"
                  :class="isDarkMode 
                    ? 'bg-green-900/30 border-green-600/40' 
                    : 'bg-green-50 border-green-300'"
                >
                  <i-mdi-check-circle 
                    class="w-5 h-5 flex-shrink-0"
                    :class="isDarkMode ? 'text-green-400' : 'text-green-600'"
                  />
                  <div class="flex-1">
                    <div 
                      class="text-xs font-medium"
                      :class="isDarkMode ? 'text-green-400' : 'text-green-700'"
                    >
                      Reporter ID (Index 0)
                    </div>
                    <div 
                      class="text-sm font-bold"
                      :class="isDarkMode ? 'text-green-300' : 'text-green-800'"
                    >
                      {{ extractedReporterId }}
                    </div>
                  </div>
                </div>
                
                <div 
                  v-if="extractedContactId" 
                  class="flex items-center gap-2 p-2 border rounded-md"
                  :class="isDarkMode 
                    ? 'bg-amber-900/30 border-amber-600/40' 
                    : 'bg-blue-50 border-blue-300'"
                >
                  <i-mdi-check-circle 
                    class="w-5 h-5 flex-shrink-0"
                    :class="isDarkMode ? 'text-amber-500' : 'text-amber-600'"
                  />
                  <div class="flex-1">
                    <div 
                      class="text-xs font-medium"
                      :class="isDarkMode ? 'text-amber-500' : 'text-amber-600'"
                    >
                      Contact ID (Index 5)
                    </div>
                    <div 
                      class="text-sm font-bold"
                      :class="isDarkMode ? 'text-amber-300' : 'text-blue-800'"
                    >
                      {{ extractedContactId }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Create Reporter Form -->
        <div 
          v-if="showCreateForm" 
          class="mt-5 p-5 border rounded-lg"
          :class="isDarkMode 
            ? 'bg-neutral-900 border-transparent' 
            : 'bg-white border-transparent'"
        >
          <div class="flex items-center justify-between mb-4">
            <h3 
              class="text-lg font-semibold"
              :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
            >
              Create New Reporter
            </h3>
            <button 
              type="button" 
              @click="closeCreateForm" 
              class="transition-colors"
              :class="isDarkMode 
                ? 'text-gray-400 hover:text-gray-100' 
                : 'text-gray-500 hover:text-gray-900'"
            >
              <i-mdi-close class="w-5 h-5" />
            </button>
          </div>

          <div class="space-y-6">
            <!-- Basic Information -->
            <div 
              class="border-b pb-4"
              :class="isDarkMode ? 'border-transparent' : 'border-transparent'"
            >
              <h4 
                class="text-md font-semibold mb-4"
                :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
              >
                Basic Information
              </h4>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label 
                    class="block text-sm font-medium mb-2"
                    :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
                  >
                    Reporter Name *
                  </label>
                  <input
                    v-model="reporterForm.fname"
                    type="text"
                    class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:border-transparent transition-all"
                    :class="isDarkMode 
                      ? 'bg-neutral-800 border-transparent text-gray-100 focus:ring-amber-500' 
                      : 'bg-gray-50 border-transparent text-gray-900 focus:ring-amber-600'"
                    placeholder="Enter reporter's full name"
                  />
                </div>

                <div>
                  <label 
                    class="block text-sm font-medium mb-2"
                    :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
                  >
                    Date of Birth
                  </label>
                  <input
                    v-model="reporterForm.dob"
                    type="date"
                    @change="handleDobChange"
                    class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:border-transparent transition-all"
                    :class="isDarkMode 
                      ? 'bg-neutral-800 border-transparent text-gray-100 focus:ring-amber-500' 
                      : 'bg-gray-50 border-transparent text-gray-900 focus:ring-amber-600'"
                  />
                  <p 
                    v-if="reporterForm.dob" 
                    class="text-xs mt-1"
                    :class="isDarkMode ? 'text-gray-400' : 'text-gray-500'"
                  >
                    Auto-fills Age and Age Group
                  </p>
                </div>

                <div>
                  <label 
                    class="block text-sm font-medium mb-2"
                    :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
                  >
                    Age
                  </label>
                  <input
                    v-model="reporterForm.age"
                    type="number"
                    :readonly="!!reporterForm.dob"
                    :class="[
                      'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:border-transparent transition-all',
                      reporterForm.dob 
                        ? isDarkMode
                          ? 'bg-gray-600 border-transparent text-gray-400 cursor-not-allowed'
                          : 'bg-gray-200 border-transparent text-gray-500 cursor-not-allowed'
                        : isDarkMode
                          ? 'bg-neutral-800 border-transparent text-gray-100 focus:ring-amber-500'
                          : 'bg-gray-50 border-transparent text-gray-900 focus:ring-amber-600'
                    ]"
                    placeholder="Age"
                  />
                </div>

                <div>
                  <BaseSelect
                    id="reporter-age-group"
                    label="Age Group"
                    v-model="reporterForm.ageGroup"
                    placeholder="Select Age Group (auto-filled from DOB)"
                    :category-id="101"
                    :disabled="!!reporterForm.dob"
                  />
                  <p 
                    v-if="reporterForm.dob" 
                    class="text-xs mt-1"
                    :class="isDarkMode ? 'text-gray-400' : 'text-gray-500'"
                  >
                    Auto-selected based on DOB
                  </p>
                </div>

                <div>
                  <BaseSelect
                    id="reporter-sex"
                    label="Sex"
                    v-model="reporterForm.sex"
                    placeholder="Select sex"
                    :category-id="120"
                  />
                </div>

                <div>
                  <BaseSelect
                    id="reporter-location"
                    label="Location"
                    v-model="reporterForm.location"
                    placeholder="Select location"
                    :category-id="88"
                  />
                </div>
              </div>
            </div>

            <!-- Contact Information -->
            <div 
              class="border-b pb-4"
              :class="isDarkMode ? 'border-transparent' : 'border-transparent'"
            >
              <h4 
                class="text-md font-semibold mb-4"
                :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
              >
                Contact Information
              </h4>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label 
                    class="block text-sm font-medium mb-2"
                    :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
                  >
                    Phone Number
                  </label>
                  <input
                    v-model="reporterForm.phone"
                    type="tel"
                    class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:border-transparent transition-all"
                    :class="isDarkMode 
                      ? 'bg-neutral-800 border-transparent text-gray-100 focus:ring-amber-500' 
                      : 'bg-gray-50 border-transparent text-gray-900 focus:ring-amber-600'"
                    placeholder="Enter phone number"
                  />
                </div>

                <div>
                  <label 
                    class="block text-sm font-medium mb-2"
                    :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
                  >
                    Alternative Phone
                  </label>
                  <input
                    v-model="reporterForm.phone2"
                    type="tel"
                    class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:border-transparent transition-all"
                    :class="isDarkMode 
                      ? 'bg-neutral-800 border-transparent text-gray-100 focus:ring-amber-500' 
                      : 'bg-gray-50 border-transparent text-gray-900 focus:ring-amber-600'"
                    placeholder="Alternative phone"
                  />
                </div>

                <div class="md:col-span-2">
                  <label 
                    class="block text-sm font-medium mb-2"
                    :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
                  >
                    Email
                  </label>
                  <input
                    v-model="reporterForm.email"
                    type="email"
                    class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:border-transparent transition-all"
                    :class="isDarkMode 
                      ? 'bg-neutral-800 border-transparent text-gray-100 focus:ring-amber-500' 
                      : 'bg-gray-50 border-transparent text-gray-900 focus:ring-amber-600'"
                    placeholder="Enter email address"
                  />
                </div>

                <div class="md:col-span-2">
                  <label 
                    class="block text-sm font-medium mb-2"
                    :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
                  >
                    Nearest Landmark
                  </label>
                  <input
                    v-model="reporterForm.landmark"
                    type="text"
                    class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:border-transparent transition-all"
                    :class="isDarkMode 
                      ? 'bg-neutral-800 border-transparent text-gray-100 focus:ring-amber-500' 
                      : 'bg-gray-50 border-transparent text-gray-900 focus:ring-amber-600'"
                    placeholder="Enter landmark"
                  />
                </div>
              </div>
            </div>

            <!-- Additional Details -->
            <div>
              <h4 
                class="text-md font-semibold mb-4"
                :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
              >
                Additional Details
              </h4>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <BaseSelect
                    id="reporter-nationality"
                    label="Nationality"
                    v-model="reporterForm.nationality"
                    placeholder="Select nationality"
                    :category-id="126"
                  />
                </div>

                <div>
                  <BaseSelect
                    id="reporter-language"
                    label="Language"
                    v-model="reporterForm.language"
                    placeholder="Select language"
                    :category-id="123"
                  />
                </div>

                <div>
                  <BaseSelect
                    id="reporter-tribe"
                    label="Tribe"
                    v-model="reporterForm.tribe"
                    placeholder="Select tribe"
                    :category-id="133"
                  />
                </div>

                <div>
                  <BaseSelect
                    id="reporter-id-type"
                    label="ID Type"
                    v-model="reporterForm.idType"
                    placeholder="Select ID type"
                    :category-id="362409"
                  />
                </div>

                <div>
                  <label 
                    class="block text-sm font-medium mb-2"
                    :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
                  >
                    ID Number
                  </label>
                  <input
                    v-model="reporterForm.idNumber"
                    type="text"
                    class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:border-transparent transition-all"
                    :class="isDarkMode 
                      ? 'bg-neutral-800 border-transparent text-gray-100 focus:ring-amber-500' 
                      : 'bg-gray-50 border-transparent text-gray-900 focus:ring-amber-600'"
                    placeholder="Enter ID number"
                  />
                </div>

                <div>
                  <label 
                    class="block text-sm font-medium mb-2"
                    :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
                  >
                    Is Refugee?
                  </label>
                  <div class="flex gap-4 mt-2">
                    <label class="flex items-center gap-1.5 cursor-pointer">
                      <input
                        v-model="reporterForm.isRefugee"
                        type="radio"
                        value="1"
                        class="w-4 h-4"
                        :class="isDarkMode ? 'text-amber-600' : 'text-amber-700'"
                      />
                      <span 
                        class="text-sm"
                        :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
                      >
                        Yes
                      </span>
                    </label>
                    <label class="flex items-center gap-1.5 cursor-pointer">
                      <input
                        v-model="reporterForm.isRefugee"
                        type="radio"
                        value="0"
                        class="w-4 h-4"
                        :class="isDarkMode ? 'text-amber-600' : 'text-amber-700'"
                      />
                      <span 
                        class="text-sm"
                        :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
                      >
                        No
                      </span>
                    </label>
                  </div>
                </div>
              </div>
            </div>

            <!-- Create Button -->
            <div 
              class="flex gap-3 justify-end pt-4 border-t"
              :class="isDarkMode ? 'border-transparent' : 'border-transparent'"
            >
              <button
                type="button"
                @click="closeCreateForm"
                class="px-4 py-2 border rounded-lg transition-colors"
                :class="isDarkMode 
                  ? 'bg-gray-700 text-gray-300 border-transparent hover:bg-gray-600' 
                  : 'bg-white text-gray-700 border-transparent hover:bg-gray-50'"
              >
                Cancel
              </button>
              <button
                type="button"
                @click="handleCreateReporter"
                :disabled="isCreating"
                class="px-4 py-2 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                :class="isDarkMode 
                  ? 'bg-amber-600 hover:bg-amber-700' 
                  : 'bg-amber-700 hover:bg-amber-800'"
              >
                <span v-if="isCreating" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                {{ isCreating ? 'Creating...' : 'Create Reporter' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="flex gap-3 justify-between mt-6">
        <button 
          type="button" 
          class="px-4 py-2 bg-transparent border rounded-lg transition-colors"
          :class="isDarkMode 
            ? 'text-gray-300 border-transparent hover:bg-gray-700 hover:border-red-500 hover:text-red-400' 
            : 'text-gray-700 border-transparent hover:bg-gray-50 hover:border-red-500 hover:text-red-600'"
          @click="$emit('cancel-form')"
        >
          Cancel
        </button>
        <div class="flex gap-3">
          <button 
            type="button" 
            class="px-4 py-2 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed" 
            :class="isDarkMode 
              ? 'bg-amber-600 hover:bg-amber-700' 
              : 'bg-amber-700 hover:bg-amber-800'"
            :disabled="!extractedReporterId || !extractedContactId"
            @click="$emit('validate-and-proceed')"
          >
            Continue
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, reactive, inject } from "vue"
import { useReporterStore } from "@/stores/reporters"
import BaseSelect from "@/components/base/BaseSelect.vue"

const props = defineProps({
  currentStep: { type: Number, required: true },
  searchQuery: { type: String, default: '' },
  filteredContacts: { type: Array, default: () => [] },
  selectedReporter: { type: Object, default: null }
})

const emit = defineEmits([
  "validate-and-proceed", 
  "cancel-form",
  "search-change",
  "select-reporter",
  "create-new-reporter",
  "reporter-created"
])

// Inject theme
const isDarkMode = inject('isDarkMode')

const reportersStore = useReporterStore()

const searchQuery = ref(props.searchQuery || "")
const debouncedQuery = ref("")
const selectedReporter = ref(props.selectedReporter)
const isLoading = ref(false)
const showCreateForm = ref(false)
const isCreating = ref(false)

// Store extracted IDs locally for display
const extractedReporterId = ref(null)  // Index 0
const extractedContactId = ref(null)   // Index 5

const reporterForm = reactive({
  fname: '',
  age: '',
  dob: '',
  ageGroup: '',
  sex: '',
  location: '',
  landmark: '',
  nationality: '',
  language: '',
  tribe: '',
  phone: '',
  phone2: '',
  email: '',
  idType: '',
  idNumber: '',
  isRefugee: '0'
})

onMounted(async () => {
  try {
    isLoading.value = true
    if (!reportersStore.reporters.length) {
      await reportersStore.listReporters()
    }
  } catch (error) {
    console.error('Error loading reporters:', error)
  } finally {
    isLoading.value = false
  }
})

let debounceTimeout
watch(searchQuery, (newVal) => {
  clearTimeout(debounceTimeout)
  debounceTimeout = setTimeout(() => {
    debouncedQuery.value = newVal.trim()
    emit('search-change', newVal.trim())
  }, 300)
})

onBeforeUnmount(() => clearTimeout(debounceTimeout))

watch(() => props.searchQuery, (newQuery) => {
  if (newQuery !== searchQuery.value) {
    searchQuery.value = newQuery
  }
})

watch(() => props.selectedReporter, (newReporter) => {
  selectedReporter.value = newReporter
})

const getFieldIndex = (fieldName) => {
  const mapping = reportersStore.reporters_k?.[`contact_${fieldName}`]
  if (mapping && Array.isArray(mapping) && mapping.length > 0) {
    return mapping[0]
  }
  const fallbackMapping = reportersStore.reporters_k?.[fieldName]
  if (fallbackMapping && Array.isArray(fallbackMapping) && fallbackMapping.length > 0) {
    return fallbackMapping[0]
  }
  return null
}

const getValue = (contact, fieldName) => {
  if (!contact || !Array.isArray(contact)) return ""
  const idx = getFieldIndex(fieldName)
  if (idx !== null && idx >= 0 && idx < contact.length) {
    return contact[idx] || ""
  }
  return ""
}

// Simple helper to get contact ID for UI purposes (search results)
const getContactId = (contact) => {
  if (!contact || !Array.isArray(contact)) return null
  const contactId = getValue(contact, 'contact_id')
  return contactId ? contactId.toString() : null
}

const shouldShowResults = computed(() => {
  return debouncedQuery.value.length >= 2
})

const filteredContacts = computed(() => {
  if (!shouldShowResults.value) return []
  const q = debouncedQuery.value.toLowerCase()
  const contacts = reportersStore.reporters || []
  const filtered = contacts.filter((contact) => {
    if (!Array.isArray(contact)) return false
    const name = getValue(contact, "fullname").toLowerCase()
    const phone = getValue(contact, "phone").toLowerCase()
    return name.includes(q) || phone.includes(q)
  })
  return filtered.slice(0, 10)
})

const handleSearchInput = (event) => {
  searchQuery.value = event.target.value
  showCreateForm.value = false
}

// ✅ CRITICAL FIX: Direct array access for existing reporter
const selectExistingReporter = (contact) => {
  selectedReporter.value = contact
  showCreateForm.value = false
  
  console.log('='.repeat(80))
  console.log('🔍 EXTRACTING IDs FROM EXISTING REPORTER')
  console.log('Full reporter array:', contact)
  
  // ✅ DIRECT ACCESS: Index 0 is ALWAYS the reporter record ID
  const reporterId = contact[0]
  console.log('📌 Index 0 (Reporter Record ID):', reporterId)
  
  // ✅ DIRECT ACCESS: Index 5 is ALWAYS the contact ID
  const contactId = contact[5]
  console.log('📌 Index 5 (Contact ID):', contactId)
  
  // Store locally for display
  extractedReporterId.value = reporterId
  extractedContactId.value = contactId
  
  console.log('✅ Extracted IDs:', {
    reporterId: reporterId,
    contactId: contactId
  })
  console.log('='.repeat(80))
  
  // Emit to parent
  emit('select-reporter', contact)
  emit('reporter-created', {
    reporterId: reporterId,
    contactId: contactId
  })
}

const openCreateReporterForm = () => {
  showCreateForm.value = true
  selectedReporter.value = null
  extractedReporterId.value = null
  extractedContactId.value = null
  searchQuery.value = ''
  emit('create-new-reporter')
}

const closeCreateForm = () => {
  showCreateForm.value = false
  Object.assign(reporterForm, {
    fname: '',
    age: '',
    dob: '',
    ageGroup: '',
    sex: '',
    location: '',
    landmark: '',
    nationality: '',
    language: '',
    tribe: '',
    phone: '',
    phone2: '',
    email: '',
    idType: '',
    idNumber: '',
    isRefugee: '0'
  })
}

const clearSelection = () => {
  selectedReporter.value = null
  extractedReporterId.value = null
  extractedContactId.value = null
  emit('select-reporter', null)
  emit('reporter-created', { reporterId: null, contactId: null })
}

const isSelected = (contact) => {
  if (!selectedReporter.value || !contact) return false
  return getContactId(contact) === getContactId(selectedReporter.value)
}

const getInitials = (name) => {
  if (!name || typeof name !== 'string') return 'NA'
  return name.split(" ")
    .map((n) => n[0] || "")
    .join("")
    .toUpperCase()
    .slice(0, 2)
}

// Age calculation helpers
const calculateAge = (dob) => {
  if (!dob) return null
  const birthDate = new Date(dob)
  const today = new Date()
  let age = today.getFullYear() - birthDate.getFullYear()
  const monthDiff = today.getMonth() - birthDate.getMonth()
  
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--
  }
  
  return age >= 0 ? Math.floor(age) : null
}

const getAgeGroupFromAge = (age) => {
  if (age === null || age < 0) return ''
  if (age < 6) return '0-5'
  if (age <= 12) return '6-12'
  if (age <= 17) return '13-17'
  if (age <= 24) return '18-24'
  if (age <= 35) return '25-35'
  if (age <= 50) return '36-50'
  return '51+'
}

const getAgeGroupId = (ageGroupText) => {
  const map = {
    '0-5': '361950',
    '6-12': '361951',
    '13-17': '361952',
    '18-24': '361953',
    '25-35': '361954',
    '36-50': '361955',
    '51+': '361956'
  }
  return map[ageGroupText] || ''
}

const handleDobChange = () => {
  if (reporterForm.dob) {
    const calculatedAge = calculateAge(reporterForm.dob)
    if (calculatedAge !== null) {
      reporterForm.age = calculatedAge.toString()
      const ageGroupText = getAgeGroupFromAge(calculatedAge)
      reporterForm.ageGroup = getAgeGroupId(ageGroupText)
    }
  } else {
    reporterForm.age = ''
    reporterForm.ageGroup = ''
  }
}

const getSexId = (sex) => {
  const map = {
    'Male': '121',
    'Female': '122',
    'Other': '123'
  }
  return map[sex] || ''
}

// ✅ CRITICAL FIX: Direct array access for new reporter
const handleCreateReporter = async () => {
  if (!reporterForm.fname || !reporterForm.fname.trim()) {
    alert('Reporter name is required')
    return
  }

  isCreating.value = true

  try {
    const timestamp = Date.now()
    const timestampSeconds = (timestamp / 1000).toFixed(3)
    const userId = "100"
    const srcUid = `walkin-${userId}-${timestamp}`
    const srcUid2 = `${srcUid}-1`
    const srcCallId = srcUid2

    const dobTimestamp = reporterForm.dob ? Math.floor(new Date(reporterForm.dob).getTime() / 1000) : ''

    const getValueOrDefault = (value, defaultValue = "") => {
      return value !== null && value !== undefined && value !== "" ? value : defaultValue
    }

    const payload = {
      ".id": "",
      src: "walkin",
      src_ts: timestampSeconds,
      src_uid: srcUid,
      src_uid2: srcUid2,
      src_callid: srcCallId,
      src_usr: userId,
      src_vector: "2",
      src_address: getValueOrDefault(reporterForm.phone),
      
      fname: reporterForm.fname,
      age_t: "0",
      age: getValueOrDefault(reporterForm.age),
      dob: dobTimestamp.toString(),
      age_group: getAgeGroupFromAge(parseInt(reporterForm.age)),
      age_group_id: getValueOrDefault(reporterForm.ageGroup),
      
      sex: reporterForm.sex ? `^${reporterForm.sex}` : "",
      sex_id: getSexId(reporterForm.sex),
      
      location_id: getValueOrDefault(reporterForm.location),
      landmark: getValueOrDefault(reporterForm.landmark),
      nationality_id: getValueOrDefault(reporterForm.nationality),
      lang_id: getValueOrDefault(reporterForm.language),
      tribe_id: getValueOrDefault(reporterForm.tribe),
      
      phone: getValueOrDefault(reporterForm.phone),
      phone2: getValueOrDefault(reporterForm.phone2),
      email: getValueOrDefault(reporterForm.email),
      
      national_id_type_id: getValueOrDefault(reporterForm.idType),
      national_id: getValueOrDefault(reporterForm.idNumber),
      
      is_refugee: getValueOrDefault(reporterForm.isRefugee, "0"),
      
      contact_uuid_id: "-1",
      disposition_id: "363034",
      activity_id: "",
      activity_ca_id: ""
    }

    const result = await reportersStore.createReporter(payload)
    
    console.log('='.repeat(80))
    console.log('🔍 EXTRACTING IDs FROM NEW REPORTER RESPONSE')
    console.log('Full response:', result)
    
    if (result && result.reporters && Array.isArray(result.reporters) && result.reporters.length > 0) {
      const reporterArray = result.reporters[0]
      console.log('Reporter array:', reporterArray)
      
      // ✅ DIRECT ACCESS: Index 0 is ALWAYS the reporter record ID
      const reporterId = reporterArray[0]
      console.log('📌 Index 0 (Reporter Record ID):', reporterId)
      
      // ✅ DIRECT ACCESS: Index 5 is ALWAYS the contact ID
      const contactId = reporterArray[5]
      console.log('📌 Index 5 (Contact ID):', contactId)
      
      // Store locally for display
      extractedReporterId.value = reporterId
      extractedContactId.value = contactId
      
      // ✅ NEW: Store the reporter array in selectedReporter so it can be displayed in Step4
      selectedReporter.value = reporterArray
      
      console.log('✅ Extracted IDs:', {
        reporterId: reporterId,
        contactId: contactId
      })
      console.log('='.repeat(80))
      
      // Emit both the IDs and the reporter data to parent
      emit('select-reporter', reporterArray)
      emit('reporter-created', {
        reporterId: reporterId,
        contactId: contactId
      })
      
      showCreateForm.value = false
      closeCreateForm()
    } else {
      throw new Error('No reporter array returned from server')
    }

  } catch (error) {
    console.error('Error creating reporter:', error)
    alert(`Failed to create reporter: ${error.message}`)
  } finally {
    isCreating.value = false
  }
}
</script>