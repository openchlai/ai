<template>
   <!-- Client Modal -->
    <div v-if="true" class="fixed top-0 left-0 w-full h-full bg-black/50 flex items-center justify-center z-[9999]">
      <div class="bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-2xl max-w-[90%] max-h-[90%] overflow-y-auto w-[95%] max-w-[95vw]">
        <div class="flex justify-between items-center p-5 border-b border-gray-300 dark:border-gray-600">
          <h3 class="m-0 text-lg font-bold text-gray-900 dark:text-gray-100">New Client</h3>
          <span class="text-2xl cursor-pointer text-gray-600 dark:text-gray-400 p-1.5 rounded transition-all hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-gray-100" @click="$emit('close-modal')">×</span>
        </div>

        <div class="p-5">
          <!-- Show existing clients -->
          <div
            v-if="clients && clients.length > 0"
            class="mb-5 p-4 bg-gray-50 dark:bg-gray-700/50 border border-gray-300 dark:border-gray-600 rounded-md"
          >
            <h4 class="m-0 mb-3 text-base font-semibold text-gray-900 dark:text-gray-100">Added Clients:</h4>
            <div
              v-for="(client, index) in clients"
              :key="index"
              class="flex justify-between items-center p-3 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md mb-2"
            >
              <span class="text-sm text-gray-900 dark:text-gray-100 font-medium">{{ client.name || 'Unnamed' }} ({{ client.age || 'Unknown age' }} {{ client.sex || 'Unknown gender' }})</span>
              <button @click="$emit('remove-client', index)" class="bg-red-600 text-white border-none px-3 py-1.5 rounded text-xs font-semibold cursor-pointer transition-all hover:bg-red-700 hover:-translate-y-px">
                Remove
              </button>
            </div>
          </div>

          <!-- Multi-step Client Form -->
          <div class="add-client-form">
            <h4 class="m-0 mb-3 text-base font-semibold text-gray-900 dark:text-gray-100">Add New Client:</h4>

            <!-- Progress Steps -->
            <div class="mb-6 py-5 border-t border-b border-gray-200 dark:border-gray-600">
              <div class="flex justify-between items-center mb-0">
                <div
                  v-for="(step, index) in clientSteps"
                  :key="index"
                  :class="[
                    'flex flex-col items-center gap-2 flex-1 relative',
                    {
                      'completed': currentClientStep > index,
                      'active': currentClientStep === index,
                      'future': currentClientStep < index,
                    },
                  ]"
                >
                  <span :class="[
                    'w-8 h-8 rounded-full flex items-center justify-center font-semibold text-sm relative z-[2]',
                    currentClientStep > index ? 'bg-green-600 text-white' : '',
                    currentClientStep === index ? 'bg-green-600 text-white' : '',
                    currentClientStep < index ? 'bg-gray-200 dark:bg-gray-600 text-gray-600 dark:text-gray-400' : ''
                  ]">
                    <span>{{ index + 1 }}</span>
                  </span>
                  <span :class="[
                    'text-xs font-medium text-center mt-1',
                    currentClientStep > index ? 'text-green-600 font-semibold' : '',
                    currentClientStep === index ? 'text-green-600 font-semibold' : '',
                    currentClientStep < index ? 'text-gray-600 dark:text-gray-400' : ''
                  ]">{{ step.title }}</span>
                  
                  <!-- Connector line -->
                  <span 
                    v-if="index < clientSteps.length - 1"
                    :class="[
                      'absolute top-4 left-1/2 right-[-50%] h-0.5 z-[1]',
                      currentClientStep > index ? 'bg-green-600' : 'bg-gray-200 dark:bg-gray-600'
                    ]"
                  ></span>
                </div>
              </div>
            </div>

            <!-- Step Content -->
            <div class="min-h-[400px]">
              <!-- Step 1: Basic Information -->
              <div v-if="currentClientStep === 0" class="py-5 animate-fadeIn">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-5 mb-6">
                  <div class="flex flex-col gap-2">
                    <label class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">Client's Name *</label>
                    <input
                      v-model="localClientForm.name"
                      type="text"
                      placeholder="Enter Client's Names"
                      class="px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 transition-all focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10"
                      @input="updateClientForm"
                    />
                  </div>

                  <div class="flex flex-col gap-2">
                    <label class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">Age</label>
                    <input
                      v-model="localClientForm.age"
                      type="number"
                      placeholder="Enter age"
                      class="px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 transition-all focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10"
                      @input="updateClientForm"
                    />
                  </div>

                  <div class="flex flex-col gap-2">
                    <label class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">DOB</label>
                    <input 
                      v-model="localClientForm.dob" 
                      type="date"
                      class="px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 transition-all focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10"
                      @input="updateClientForm"
                    />
                  </div>

                  <div class="flex flex-col gap-2">
                    <BaseSelect
                      id="client-age-group"
                      label="Age Group"
                      v-model="localClientForm.ageGroup"
                      placeholder="Select Age Group"
                      :category-id="101"
                    />
                  </div>

                  <div class="flex flex-col gap-2">
                    <BaseSelect
                      id="client-location"
                      label="Location"
                      v-model="localClientForm.location"
                      placeholder="Select Location"
                      :category-id="88"
                    />
                  </div>

                  <div class="flex flex-col gap-2">
                    <BaseSelect
                      id="client-sex"
                      label="Sex"
                      v-model="localClientForm.sex"
                      placeholder="Select Gender"
                      :category-id="120"
                    />
                  </div>
                </div>
              </div>

              <!-- Step 2: Contact & Identity -->
              <div v-if="currentClientStep === 1" class="py-5 animate-fadeIn">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-5 mb-6">
                  <div class="flex flex-col gap-2">
                    <label class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">Nearest Landmark</label>
                    <input
                      v-model="localClientForm.landmark"
                      type="text"
                      placeholder="Enter Nearest Landmark"
                      class="px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 transition-all focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10"
                      @input="updateClientForm"
                    />
                  </div>

                  <div class="flex flex-col gap-2">
                    <BaseSelect
                      id="client-nationality"
                      label="Nationality"
                      v-model="localClientForm.nationality"
                      placeholder="Select Nationality"
                      :category-id="126"
                    />
                  </div>

                  <div class="flex flex-col gap-2">
                    <BaseSelect
                      id="client-id-type"
                      label="ID Type"
                      v-model="localClientForm.idType"
                      placeholder="Select ID Type"
                      :category-id="362409"
                    />
                  </div>

                  <div class="flex flex-col gap-2">
                    <label class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">ID Number</label>
                    <input
                      v-model="localClientForm.idNumber"
                      type="text"
                      placeholder="Enter ID Number"
                      class="px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 transition-all focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10"
                      @input="updateClientForm"
                    />
                  </div>

                  <div class="flex flex-col gap-2">
                    <BaseSelect
                      id="client-language"
                      label="Language"
                      v-model="localClientForm.language"
                      placeholder="Select Language"
                      :category-id="123"
                    />
                  </div>

                  <div class="flex flex-col gap-2">
                    <label class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">Is the Client a Refugee?</label>
                    <div class="flex gap-4 flex-wrap">
                      <label class="flex items-center gap-1.5 cursor-pointer">
                        <input
                          type="radio"
                          v-model="localClientForm.isRefugee"
                          value="yes"
                          @change="updateClientForm"
                        />
                        <span class="text-sm text-gray-900 dark:text-gray-100">Yes</span>
                      </label>
                      <label class="flex items-center gap-1.5 cursor-pointer">
                        <input
                          type="radio"
                          v-model="localClientForm.isRefugee"
                          value="no"
                          @change="updateClientForm"
                        />
                        <span class="text-sm text-gray-900 dark:text-gray-100">No</span>
                      </label>
                      <label class="flex items-center gap-1.5 cursor-pointer">
                        <input
                          type="radio"
                          v-model="localClientForm.isRefugee"
                          value="unknown"
                          @change="updateClientForm"
                        />
                        <span class="text-sm text-gray-900 dark:text-gray-100">Unknown</span>
                      </label>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Step 3: Contact Information -->
              <div v-if="currentClientStep === 2" class="py-5 animate-fadeIn">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-5 mb-6">
                  <div class="flex flex-col gap-2">
                    <BaseSelect
                      id="client-tribe"
                      label="Tribe"
                      v-model="localClientForm.tribe"
                      placeholder="Select Tribe"
                      :category-id="133"
                    />
                  </div>

                  <div class="flex flex-col gap-2">
                    <label class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">Phone Number</label>
                    <input
                      v-model="localClientForm.phone"
                      type="tel"
                      placeholder="Enter Phone Number"
                      class="px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 transition-all focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10"
                      @input="updateClientForm"
                    />
                  </div>

                  <div class="flex flex-col gap-2">
                    <label class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">Alternative Phone</label>
                    <input
                      v-model="localClientForm.alternativePhone"
                      type="tel"
                      placeholder="Enter Alternate Phone Number"
                      class="px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 transition-all focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10"
                      @input="updateClientForm"
                    />
                  </div>

                  <div class="flex flex-col gap-2">
                    <label class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">Email</label>
                    <input
                      v-model="localClientForm.email"
                      type="email"
                      placeholder="Enter Email Address"
                      class="px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 transition-all focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10"
                      @input="updateClientForm"
                    />
                  </div>

                  <div class="flex flex-col gap-2">
                    <BaseSelect
                      id="Reporter's Relationship with Client"
                      label="Reporter's Relationship with Client"
                      v-model="localClientForm.relationship"
                      placeholder=""
                      :category-id="236634"
                    />
                  </div>

                  <div class="flex flex-col gap-2">
                    <label class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">Relationship Comment</label>
                    <textarea
                      v-model="localClientForm.relationshipComment"
                      placeholder="Enter Comments about the relationship"
                      rows="3"
                      class="px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 transition-all focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10"
                      @input="updateClientForm"
                    ></textarea>
                  </div>
                </div>
              </div>

              <!-- Step 4: Household & Background -->
              <div v-if="currentClientStep === 3" class="py-5 animate-fadeIn">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-5 mb-6">
                  <div class="flex flex-col gap-2">
                    <label class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">Number of Adults in Household</label>
                    <input
                      v-model="localClientForm.adultsInHousehold"
                      type="number"
                      placeholder="Enter number"
                      class="px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 transition-all focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10"
                      @input="updateClientForm"
                    />
                  </div>

                  <div class="flex flex-col gap-2">
                    <BaseSelect
                      id="Household Type"
                      label="Relationship with Client?"
                      v-model="localClientForm.householdType"
                      placeholder=""
                      :category-id="236634"
                    />
                  </div>

                  <div class="flex flex-col gap-2">
                    <BaseSelect
                      id="Head of Household Occupation"
                      label="Head of Household Occupation"
                      v-model="localClientForm.headOccupation"
                      placeholder=""
                      :category-id="236648"
                    />
                  </div>

                  <div class="flex flex-col gap-2">
                    <label class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">Parent/Guardian's Name</label>
                    <input
                      v-model="localClientForm.parentGuardianName"
                      type="text"
                      placeholder="Enter name"
                      class="px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 transition-all focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10"
                      @input="updateClientForm"
                    />
                  </div>

                  <div class="flex flex-col gap-2">
                    <BaseSelect
                      id="Parent/Guardian's Marital Status"
                      label="Parent/Guardian's Marital Status"
                      v-model="localClientForm.parentMaritalStatus"
                      placeholder=""
                      :category-id="236654"
                    />
                  </div>

                  <div class="flex flex-col gap-2">
                    <BaseSelect
                      id="Household Type"
                      label="Household Type"
                      v-model="localClientForm.HouseholdType"
                      placeholder="Household Type"
                      :category-id="236674"
                    />
                  </div>

                  <div class="flex flex-col gap-2">
                    <label class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">Parent/Guardian's Identification Number</label>
                    <input
                      v-model="localClientForm.parentIdNumber"
                      type="text"
                      placeholder="Enter ID number"
                      class="px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 transition-all focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10"
                      @input="updateClientForm"
                    />
                  </div>
                </div>
              </div>

              <!-- Step 5: Health & Status -->
              <div v-if="currentClientStep === 4" class="py-5 animate-fadeIn">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-5 mb-6">
                  <div class="flex flex-col gap-2">
                    <BaseSelect
                      id="Client's Health Status"
                      label="Client's Health Status"
                      v-model="localClientForm.healthStatus"
                      placeholder=""
                      :category-id="236660"
                    />
                  </div>

                  <div class="flex flex-col gap-2">
                    <BaseSelect
                      id="Client's HIV Status"
                      label="Client's HIV Status"
                      v-model="localClientForm.hivStatus"
                      placeholder=""
                      :category-id="105"
                    />
                  </div>

                  <div class="flex flex-col gap-2">
                    <BaseSelect
                      id="Client's Marital Status"
                      label="Client's Marital Status"
                      v-model="localClientForm.maritalStatus"
                      placeholder=""
                      :category-id="236654"
                      @change="updateClientForm"
                    />

                    <!-- Conditional Fields: Spouse Details -->
                    <div v-if="showSpouseFields" class="mt-4 p-4 bg-gray-50 dark:bg-gray-700/50 border border-gray-300 dark:border-gray-600 rounded-md">
                      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="flex flex-col gap-2">
                          <label class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">Spouse Name</label>
                          <input
                            v-model="localClientForm.spouseName"
                            type="text"
                            placeholder="Enter spouse's name"
                            class="px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 transition-all focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10"
                            @input="updateClientForm"
                          />
                        </div>
                        
                        <div class="flex flex-col gap-2">
                          <BaseSelect
                            id="spouse-profession"
                            label="Spouse Profession"
                            v-model="localClientForm.spouseProfession"
                            placeholder="Select spouse's profession"
                            :category-id="236648"
                            @change="updateClientForm"
                          />
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="flex flex-col gap-2">
                    <label class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">Is the Client Attending School?</label>
                    <div class="flex gap-4 flex-wrap">
                      <label class="flex items-center gap-1.5 cursor-pointer">
                        <input
                          type="radio"
                          v-model="localClientForm.attendingSchool"
                          value="yes"
                          @change="updateClientForm"
                        />
                        <span class="text-sm text-gray-900 dark:text-gray-100">Yes</span>
                      </label>
                      <label class="flex items-center gap-1.5 cursor-pointer">
                        <input
                          type="radio"
                          v-model="localClientForm.attendingSchool"
                          value="no"
                          @change="updateClientForm"
                        />
                        <span class="text-sm text-gray-900 dark:text-gray-100">No</span>
                      </label>
                      <label class="flex items-center gap-1.5 cursor-pointer">
                        <input
                          type="radio"
                          v-model="localClientForm.attendingSchool"
                          value="unknown"
                          @change="updateClientForm"
                        />
                        <span class="text-sm text-gray-900 dark:text-gray-100">Unknown</span>
                      </label>
                    </div>

                    <!-- School fields when attending YES -->
                    <div v-if="localClientForm.attendingSchool === 'yes'" class="mt-4 p-4 bg-gray-50 dark:bg-gray-700/50 border border-gray-300 dark:border-gray-600 rounded-md">
                      <div class="grid grid-cols-1 gap-3">
                        <div class="flex flex-col gap-2">
                          <label class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">School Name</label>
                          <input
                            v-model="localClientForm.schoolName"
                            type="text"
                            placeholder="Enter school name"
                            class="px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 transition-all focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10"
                            @input="updateClientForm"
                          />
                        </div>

                        <div class="flex flex-col gap-2">
                          <label class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">School Address</label>
                          <input
                            v-model="localClientForm.schoolAddress"
                            type="text"
                            placeholder="Enter school address"
                            class="px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 transition-all focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10"
                            @input="updateClientForm"
                          />
                        </div>

                        <div class="flex flex-col gap-2">
                          <BaseSelect
                            id="school-level"
                            label="School Level"
                            v-model="localClientForm.schoolLevel"
                            placeholder="Select school level"
                            :category-id="236712"
                            @change="updateClientForm"
                          />
                        </div>

                        <div class="flex flex-col gap-2">
                          <BaseSelect
                            id="school-type"
                            label="School Type"
                            v-model="localClientForm.schoolType"
                            placeholder="Select school type"
                            :category-id="236711"
                            @change="updateClientForm"
                          />
                        </div>

                        <div class="flex flex-col gap-2">
                          <label class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">School Attendance</label>
                          <input
                            v-model="localClientForm.schoolAttendance"
                            type="text"
                            placeholder="Enter attendance pattern (e.g., Regular, Irregular)"
                            class="px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 transition-all focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10"
                            @input="updateClientForm"
                          />
                        </div>
                      </div>
                    </div>

                    <!-- Reason for not attending when NO -->
                    <div v-if="localClientForm.attendingSchool === 'no'" class="mt-4 p-4 bg-gray-50 dark:bg-gray-700/50 border border-gray-300 dark:border-gray-600 rounded-md">
                      <div class="flex flex-col gap-2">
                        <label class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">Reason for Not Attending School</label>
                        <input
                          v-model="localClientForm.reasonNotAttending"
                          type="text"
                          placeholder="Enter reason for not attending school"
                          class="px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 transition-all focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10"
                          @input="updateClientForm"
                        />
                      </div>
                    </div>
                  </div>

                  <div class="flex flex-col gap-2">
                    <label class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">Is the Client Disabled?</label>
                    <div class="flex gap-4 flex-wrap">
                      <label class="flex items-center gap-1.5 cursor-pointer">
                        <input
                          type="radio"
                          v-model="localClientForm.isDisabled"
                          value="yes"
                          @change="updateClientForm"
                        />
                        <span class="text-sm text-gray-900 dark:text-gray-100">Yes</span>
                      </label>
                      <label class="flex items-center gap-1.5 cursor-pointer">
                        <input
                          type="radio"
                          v-model="localClientForm.isDisabled"
                          value="no"
                          @change="updateClientForm"
                        />
                        <span class="text-sm text-gray-900 dark:text-gray-100">No</span>
                      </label>
                      <label class="flex items-center gap-1.5 cursor-pointer">
                        <input
                          type="radio"
                          v-model="localClientForm.isDisabled"
                          value="unknown"
                          @change="updateClientForm"
                        />
                        <span class="text-sm text-gray-900 dark:text-gray-100">Unknown</span>
                      </label>
                    </div>

                    <!-- Disability details when disabled YES -->
                    <div v-if="localClientForm.isDisabled === 'yes'" class="mt-4 p-4 bg-gray-50 dark:bg-gray-700/50 border border-gray-300 dark:border-gray-600 rounded-md">
                      <div class="grid grid-cols-1 gap-3">
                        <div class="flex flex-col gap-2">
                          <BaseSelect
                            id="disability-type"
                            label="Type of Disability"
                            v-model="localClientForm.disability"
                            placeholder="Select type of disability"
                            :category-id="236669"
                            @change="updateClientForm"
                          />
                        </div>

                        <div class="flex flex-col gap-2">
                          <label class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">Special Services Required?</label>
                          <div class="flex gap-4">
                            <label class="flex items-center gap-1.5 cursor-pointer">
                              <input
                                type="radio"
                                v-model="localClientForm.specialServicesRequired"
                                value="yes"
                                @change="updateClientForm"
                              />
                              <span class="text-sm text-gray-900 dark:text-gray-100">Yes</span>
                            </label>
                            <label class="flex items-center gap-1.5 cursor-pointer">
                              <input
                                type="radio"
                                v-model="localClientForm.specialServicesRequired"
                                value="no"
                                @change="updateClientForm"
                              />
                              <span class="text-sm text-gray-900 dark:text-gray-100">No</span>
                            </label>
                          </div>

                          <!-- Referrals field when special services YES -->
                          <div v-if="localClientForm.specialServicesRequired === 'yes'" class="mt-4 p-4 bg-gray-50 dark:bg-gray-700/50 border border-gray-300 dark:border-gray-600 rounded-md">
                            <div class="flex flex-col gap-2">
                              <BaseOptions
                                id="disability-referrals"
                                label="Referrals Needed"
                                v-model="localClientForm.disabilityReferrals"
                                placeholder="Select referral types..."
                                :category-id="236707"
                                @selection-change="updateClientForm"
                              />
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Step Navigation -->
            <div class="flex justify-between items-center mt-6 pt-5 border-t border-gray-300 dark:border-gray-600">
              <button
                v-if="currentClientStep > 0"
                @click="$emit('prev-client-step')"
                type="button"
                class="px-5 py-2.5 border-none rounded-md font-medium cursor-pointer transition-all bg-gray-600 text-white hover:bg-gray-700"
              >
                Previous
              </button>
              <button
                v-if="currentClientStep < clientSteps.length - 1"
                @click="$emit('next-client-step')"
                type="button"
                class="px-5 py-2.5 border-none rounded-md font-medium cursor-pointer transition-all bg-blue-600 text-white hover:bg-blue-700"
              >
                Next
              </button>
              <button
                v-if="currentClientStep === clientSteps.length - 1"
                @click="handleAddClient"
                type="button"
                class="px-5 py-2.5 border-none rounded-md font-medium cursor-pointer transition-all bg-blue-600 text-white hover:bg-blue-700"
              >
                Add Client
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
</template>

<script setup>
import { ref, reactive, watch, computed } from "vue";
import BaseSelect from "@/components/base/BaseSelect.vue";
import BaseOptions from "@/components/base/BaseOptions.vue";

// Props - receive data from parent
const props = defineProps({
  clients: { type: Array, default: () => [] },
  clientForm: { type: Object, required: true },
  currentClientStep: { type: Number, default: 0 },
  showSpecialServicesDropdown: { type: Boolean, default: false },
  specialServicesSearch: { type: String, default: '' },
  filteredSpecialServices: { type: Array, default: () => [] }
});

// Emits - communicate with parent
const emit = defineEmits([
  'close-modal',
  'remove-client',
  'update-client-form',
  'toggle-special-services-dropdown',
  'prev-client-step',
  'next-client-step',
  'add-client'
]);

const localClientForm = reactive({ 
  ...props.clientForm,
  attendingSchool: props.clientForm.attendingSchool || '',
  schoolName: props.clientForm.schoolName || '',
  schoolAddress: props.clientForm.schoolAddress || '',
  schoolLevel: props.clientForm.schoolLevel || '',
  schoolType: props.clientForm.schoolType || '',
  schoolAttendance: props.clientForm.schoolAttendance || '',
  reasonNotAttending: props.clientForm.reasonNotAttending || '',
  isDisabled: props.clientForm.isDisabled || '',
  disability: props.clientForm.disability || '',
  specialServicesRequired: props.clientForm.specialServicesRequired || '',
  disabilityReferrals: props.clientForm.disabilityReferrals || [],
  spouseName: props.clientForm.spouseName || '',
  spouseProfession: props.clientForm.spouseProfession || '',
  dob: props.clientForm.dob || ''
});

// Watch for changes from parent
watch(() => props.clientForm, (newForm) => {
  Object.assign(localClientForm, newForm);
}, { deep: true });

const singleStatusValues = [
  'single', 'Single', 'SINGLE',
  'unknown', 'Unknown', 'UNKNOWN',
  'unmarried', 'Unmarried',
  'never married', 'Never Married',
];

const showSpouseFields = computed(() => {
  const maritalStatus = localClientForm.maritalStatus;
  if (!maritalStatus) return false;
  
  const statusValue = String(maritalStatus);
  const isSingleOrUnknown = singleStatusValues.some(singleStatus => {
    return statusValue.toLowerCase() === String(singleStatus).toLowerCase();
  });
  
  return !isSingleOrUnknown;
});

const updateClientForm = () => {
  emit('update-client-form', { ...localClientForm });
};

const handleAddClient = () => {
  console.log('Adding client with complete data:', localClientForm);
  
  if (!localClientForm.name) {
    alert('Client name is required');
    return;
  }
  
  emit('add-client');
};

const clientSteps = [
  { title: "Basic Information" },
  { title: "Contact & Identity" },
  { title: "Contact Information" },
  { title: "Household & Background" },
  { title: "Health & Status" },
];
</script>

<style scoped>
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fadeIn {
  animation: fadeIn 0.3s ease-in-out;
}
</style>