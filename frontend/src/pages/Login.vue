<template>
  <div class="login-outer-wrapper">
    <div class="login-container">
      <div class="side-panel left-panel">
        <!-- decorative left rail hidden on desktop in new design -->
        <div class="flag-strip left-flag"></div>
        <div class="pattern-bg pattern-bg-left"></div>
      </div>
      <div class="center-panel">
        <div class="form-section">
          <div class="coat-of-arms-container">
            <img src="@/assets/images/coat of arms.png" alt="Kenya Coat of Arms" class="coat-of-arms" />
          </div>
          <h2 class="form-title">
            <span v-if="currentStep === 'email'">
              Welcome home
            </span>
            <span v-else-if="currentStep === 'otp'">Enter verification code</span>
            <span v-else-if="currentStep === 'password'">Enter your password</span>
          </h2>
          <p v-if="currentStep === 'email'" class="form-subtitle">Please enter your details.</p>
          <div class="step-indicator">
            <div class="step" :class="{ active: currentStep === 'email', completed: currentStep === 'otp' || currentStep === 'password' }">
              <span class="step-number">1</span>
              <span class="step-label">{{ getContactLabel() }}</span>
            </div>
            <div class="step-divider"></div>
            <div class="step" :class="{ active: currentStep === 'otp' || currentStep === 'password' }">
              <span class="step-number">2</span>
              <span class="step-label">{{ authMethod === 'otp' ? 'Verify' : 'Password' }}</span>
            </div>
          </div>
          <form @submit.prevent="handleSubmit" class="login-form">
            <!-- Error Message -->
            <div v-if="error" class="error-message">
              {{ error }}
            </div>

            <!-- Success Message -->
            <div v-if="successMessage" class="success-message">
              {{ successMessage }}
            </div>

            <!-- Step 1: Contact Info and Login Method Selection -->
            <div v-if="currentStep === 'email'" class="step-content">
              <!-- Dynamic Contact Input -->
              <div class="input-group">
                <label class="input-label">{{ getContactLabel() }}</label>
                <input 
                  :type="getInputType()" 
                  v-model="contactInfo" 
                  class="form-input"
                  :class="{ 'input-error': submitted && !contactInfo }" 
                  :placeholder="getInputPlaceholder()" 
                  required
                  :disabled="loading">
                <div v-if="submitted && !contactInfo" class="validation-error">
                  {{ getContactLabel() }} is required
                </div>
              </div>

              <!-- Login Method Selection -->
              <div class="input-group">
                <label class="input-label">How would you like to log in?</label>
                <div class="login-method-container">
                  <div class="method-option" 
                       :class="{ active: loginMethod === 'password' }"
                       @click="selectLoginMethod('password')">
                    <div class="method-icon">🔐</div>
                    <div class="method-info">
                      <div class="method-title">Password</div>
                      <div class="method-desc">Use your password</div>
                    </div>
                  </div>
                  <div class="method-option" 
                       :class="{ active: loginMethod === 'otp' }"
                       @click="selectLoginMethod('otp')">
                    <div class="method-icon">📧</div>
                    <div class="method-info">
                      <div class="method-title">OTP</div>
                      <div class="method-desc">Get verification code</div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Password Input (if password method selected) -->
              <div v-if="loginMethod === 'password'" class="input-group">
                <label class="input-label">Password</label>
                <div class="password-input-container">
                  <input 
                    :type="showPassword ? 'text' : 'password'" 
                    v-model="password" 
                    class="form-input"
                    :class="{ 'input-error': submitted && loginMethod === 'password' && !password }" 
                    placeholder="Enter your password" 
                    :disabled="loading">
                  <button 
                    type="button" 
                    class="password-toggle-button" 
                    @click="showPassword = !showPassword"
                    :disabled="loading">
                    <span v-if="showPassword">👁️</span>
                    <span v-else>👁️‍🗨️</span>
                  </button>
                </div>
                <div v-if="submitted && loginMethod === 'password' && !password" class="validation-error">
                  Password is required
                </div>
              </div>

              <!-- OTP Delivery Method (if OTP method selected) -->
              <div v-if="loginMethod === 'otp'" class="input-group">
                <label class="input-label">How to receive OTP</label>
                <div class="select-container">
                  <select v-model="deliveryMethod" class="form-select"
                    :class="{ 'input-error': submitted && loginMethod === 'otp' && !deliveryMethod }" 
                    :disabled="loading"
                    @change="handleDeliveryMethodChange">
                    <option value="">Select delivery method</option>
                    <option value="email">📧 Email</option>
                    <option value="sms">📱 SMS</option>
                    <option value="whatsapp">💬 WhatsApp</option>
                  </select>
                  <div class="select-arrow">
                    <svg xmlns="http://www.w3.org/2000/svg" class="arrow-icon" viewBox="0 0 24 24" fill="none"
                      stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <polyline points="6,9 12,15 18,9"></polyline>
                    </svg>
                  </div>
                </div>
                <div v-if="submitted && loginMethod === 'otp' && !deliveryMethod" class="validation-error">
                  Please select a delivery method
                </div>

                <!-- Delivery Method Description -->
                <div v-if="deliveryMethod" class="means-description">
                  <p v-if="deliveryMethod === 'email'" class="means-text">
                    📧 OTP will be sent to your email address
                  </p>
                  <p v-else-if="deliveryMethod === 'sms'" class="means-text">
                    📱 OTP will be sent via SMS to your phone number
                  </p>
                  <p v-else-if="deliveryMethod === 'whatsapp'" class="means-text">
                    💬 OTP will be sent via WhatsApp to your phone number
                  </p>
                </div>
              </div>

              <!-- Remember / Forgot row -->
              <div class="remember-forgot-row">
                <div class="remember-me">
                  <label class="checkbox-container">
                    <input type="checkbox" v-model="rememberMe" :disabled="loading">
                    <span class="checkmark"></span>
                    Remember me for 30 days
                  </label>
                </div>
                <a href="#" class="forgot-inline" @click.prevent="handleForgotPassword">Forgot password?</a>
              </div>
            </div>

            <!-- Step 2: OTP Input -->
            <div v-if="currentStep === 'otp'" class="step-content">
              <div class="otp-info">
                <div class="selected-means-display">
                  <div class="means-icon">
                    <span v-if="deliveryMethod === 'sms'">📱</span>
                    <span v-else-if="deliveryMethod === 'email'">📧</span>
                    <span v-else-if="deliveryMethod === 'whatsapp'">💬</span>
                  </div>
                  <p class="otp-message">
                    We've sent a 6-digit verification code to your 
                    <span v-if="deliveryMethod === 'email'">email address <strong>{{ maskedContact }}</strong></span>
                    <span v-else-if="deliveryMethod === 'sms'">phone number <strong>{{ maskedContact }}</strong></span>
                    <span v-else-if="deliveryMethod === 'whatsapp'">WhatsApp number <strong>{{ maskedContact }}</strong></span>
                  </p>
                </div>
              </div>

              <div class="input-group">
                <label class="input-label">Enter 6-digit OTP</label>
                <div class="otp-input-container">
                  <input v-for="(digit, index) in otpDigits" :key="index" type="text" maxlength="1"
                    v-model="otpDigits[index]" @input="handleOtpInput(index, $event)"
                    @keydown="handleOtpKeydown(index, $event)" :ref="el => otpInputs[index] = el" class="otp-input"
                    :class="{ 'input-error': submitted && !isOtpComplete }" :disabled="loading">
                </div>
                <div v-if="submitted && !isOtpComplete" class="validation-error">
                  Please enter the complete 6-digit OTP
                </div>
              </div>

              <!-- Resend OTP -->
              <div class="resend-container">
                <span v-if="resendTimer > 0" class="resend-timer">
                  Resend OTP in {{ resendTimer }}s
                </span>
                <button v-else type="button" class="resend-button" @click="resendOtp" :disabled="loading">
                  <span v-if="deliveryMethod === 'sms'">📱 Resend SMS</span>
                  <span v-else-if="deliveryMethod === 'email'">📧 Resend Email</span>
                  <span v-else-if="deliveryMethod === 'whatsapp'">💬 Resend WhatsApp</span>
                </button>
              </div>

              <!-- Back to Contact Info -->
              <button type="button" class="back-button" @click="goBackToEmail" :disabled="loading">
                <span class="back-arrow">←</span>
                <span>Back to {{ getContactLabel() }}</span>
              </button>
            </div>

            <!-- Submit Button -->
            <button type="submit" class="login-button" :disabled="loading || !isFormValid">
              <span v-if="!loading">
                <span v-if="currentStep === 'email' && loginMethod === 'password'">Login</span>
                <span v-else-if="currentStep === 'email' && loginMethod === 'otp'">Send OTP</span>
                <span v-else-if="currentStep === 'otp'">Verify & Login</span>
              </span>
              <span v-else class="loading-content">
                <div class="spinner"></div>
                <span v-if="currentStep === 'email' && loginMethod === 'password'">Logging in...</span>
                <span v-else-if="currentStep === 'email' && loginMethod === 'otp'">Sending OTP...</span>
                <span v-else-if="currentStep === 'otp'">Verifying...</span>
              </span>
            </button>
          </form>

          <!-- Social Sign-in -->
          <div class="divider"><span>or</span></div>
          <div class="social-row">
            <button type="button" class="social-btn" aria-label="Sign in with Apple"></button>
            <button type="button" class="social-btn" aria-label="Sign in with Google">G</button>
            <button type="button" class="social-btn" aria-label="Sign in with Facebook">f</button>
          </div>

          <!-- Help Text -->
          <div class="help-text">
            Need help? <a href="#" class="help-link" @click.prevent="handleHelp">Contact Support</a>
          </div>
          <!-- Partners section below help text -->
          <div class="partners-section partners-section-noframe">
            <div class="partners-label partners-label-colored">
              <span class="c-black">O</span><span class="c-red">u</span><span class="c-green">r</span>
              <span class="c-black"> </span>
              <span class="c-red">P</span><span class="c-green">a</span><span class="c-black">r</span><span class="c-red">t</span><span class="c-green">n</span><span class="c-black">e</span><span class="c-red">r</span><span class="c-green">s</span>
            </div>
            <div class="partners-logos-row">
              <img src="@/assets/images/welcome-helpline.png" alt="Childline Kenya" class="partner-logo" />
              <img src="@/assets/images/MOH.png" alt="Ministry of Health" class="partner-logo" />
              <img src="@/assets/images/unicef.png" alt="UNICEF" class="partner-logo" />
              <img src="@/assets/images/GIZ.png" alt="GIZ" class="partner-logo" />
              <img src="@/assets/images/UNFPA.png" alt="UNFPA" class="partner-logo" />
            </div>
          </div>
        </div>
      </div>
      <div class="side-panel right-panel">
        <!-- hero visual panel -->
        <div class="hero-panel" aria-hidden="true"></div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
// import axiosInstance from '../utils/axios';

export default {
  setup() {
    const router = useRouter();
    const route = useRoute();

    // Environment variables
    const config = {
      apiBaseUrl: import.meta.env.VITE_API_BASE_URL,
      apiTimeout: parseInt(import.meta.env.VITE_API_TIMEOUT) || 10000,
      sipUri: import.meta.env.VITE_SIP_URI,
      sipPassword: import.meta.env.VITE_SIP_PASSWORD,
      sipWebsocketUrl: import.meta.env.VITE_SIP_WEBSOCKET_URL,
      sipCheckWebsocketUrl: import.meta.env.VITE_SIP_CHECK_WEBSOCKET_URL,
      defaultReturnUrl: import.meta.env.VITE_DEFAULT_RETURN_URL || '/dashboard',
      otpResendTimer: parseInt(import.meta.env.VITE_OTP_RESEND_TIMER) || 30,
      successMessageDuration: parseInt(import.meta.env.VITE_SUCCESS_MESSAGE_DURATION) || 3000,
      mockApiDelay: parseInt(import.meta.env.VITE_MOCK_API_DELAY) || 1000,
      enableMockApi: import.meta.env.VITE_ENABLE_MOCK_API === 'true',
      appName: import.meta.env.VITE_APP_NAME,
      helpUrl: import.meta.env.VITE_HELP_URL
    };

    // Form data
    const contactInfo = ref(''); // This will hold email or phone based on delivery method
    const password = ref('');
    const loginMethod = ref('otp'); // 'password' or 'otp'
    const deliveryMethod = ref(''); // 'email', 'sms', 'whatsapp'
    const rememberMe = ref(false);
    const otpDigits = ref(['', '', '', '', '', '']);
    const otpInputs = ref([]);
    const showPassword = ref(false);

    // Form state
    const currentStep = ref('email');
    const loading = ref(false);
    const submitted = ref(false);
    const error = ref('');
    const successMessage = ref('');
    const returnUrl = ref(route.query.returnUrl || config.defaultReturnUrl);
    const resendTimer = ref(0);
    const resendInterval = ref(null);
    const userId = ref('');
    const maskedContact = ref('');

    // SIP Details - using environment variables
    const sipConnectionDetails = ref({
      uri: config.sipUri,
      password: config.sipPassword,
      websocketURL: config.sipWebsocketUrl
    });

    // Computed properties
    const isOtpComplete = computed(() => {
      return otpDigits.value.every(digit => digit !== '');
    });

    const isFormValid = computed(() => {
      if (currentStep.value === 'email') {
        if (loginMethod.value === 'password') {
          return contactInfo.value.length > 0 && password.value.length > 0;
        } else if (loginMethod.value === 'otp') {
          return contactInfo.value.length > 0 && deliveryMethod.value !== '';
        }
      } else if (currentStep.value === 'otp') {
        return isOtpComplete.value;
      }
      return false;
    });

    // Helper methods for dynamic input handling
    const getContactLabel = () => {
      if (deliveryMethod.value === 'sms' || deliveryMethod.value === 'whatsapp') {
        return 'Phone Number';
      }
      return 'Email Address';
    };

    const getInputType = () => {
      if (deliveryMethod.value === 'sms' || deliveryMethod.value === 'whatsapp') {
        return 'tel';
      }
      return 'email';
    };

    const getInputPlaceholder = () => {
      if (deliveryMethod.value === 'sms' || deliveryMethod.value === 'whatsapp') {
        return 'Enter your phone number';
      }
      return 'Enter your email address';
    };

    const validateContactInfo = () => {
      if (deliveryMethod.value === 'sms' || deliveryMethod.value === 'whatsapp') {
        // Enhanced phone number validation
        const phoneRegex = /^[\+]?[1-9][\d]{7,15}$/;
        const cleanPhone = contactInfo.value.replace(/[\s\-$$$$]/g, '');
        return phoneRegex.test(cleanPhone);
      } else {
        // Enhanced email validation
        const emailRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;
        return emailRegex.test(contactInfo.value.trim());
      }
    };

    // Methods
    const selectLoginMethod = (method) => {
      loginMethod.value = method;
      error.value = '';
      // Reset delivery method when switching to password
      if (method === 'password') {
        deliveryMethod.value = 'email';
        contactInfo.value = '';
      }
    };

    const handleDeliveryMethodChange = () => {
      // Clear contact info when delivery method changes to force re-entry
      contactInfo.value = '';
      error.value = '';
    };

    const handleOtpInput = (index, event) => {
      const value = event.target.value;
      if (value && index < 5) {
        otpInputs.value[index + 1]?.focus();
      }
    };

    const handleOtpKeydown = (index, event) => {
      if (event.key === 'Backspace' && !otpDigits.value[index] && index > 0) {
        otpInputs.value[index - 1]?.focus();
      }
    };

    const startResendTimer = () => {
      resendTimer.value = config.otpResendTimer;
      resendInterval.value = setInterval(() => {
        resendTimer.value--;
        if (resendTimer.value <= 0) {
          clearInterval(resendInterval.value);
        }
      }, 1000);
    };

    const maskContactInfo = (contact) => {
      if (deliveryMethod.value === 'sms' || deliveryMethod.value === 'whatsapp') {
        // Mask phone number
        return contact.length > 4 ? '***' + contact.slice(-4) : contact;
      } else {
        // Mask email
        const [username, domain] = contact.split('@');
        const maskedUsername = username.length > 2 
          ? username.substring(0, 2) + '*'.repeat(username.length - 2)
          : username;
        return `${maskedUsername}@${domain}`;
      }
    };

    const passwordLogin = async () => {
      loading.value = true;
      error.value = '';

      // Validate contact info
      if (!validateContactInfo()) {
        error.value = `Please enter a valid ${getContactLabel().toLowerCase()}`;
        loading.value = false;
        return;
      }

      try {
        if (config.enableMockApi) {
          // Mock API call - replace with actual axios call
          await new Promise(resolve => setTimeout(resolve, config.mockApiDelay));
          
          // Simulate successful login
          const mockResponse = {
            access_token: 'mock_access_token',
            refresh_token: 'mock_refresh_token',
            user: { id: 1, name: 'Test User' },
            session_id: 'mock_session_id'
          };

          // Store authentication tokens and user data
          localStorage.setItem('access_token', mockResponse.access_token);
          localStorage.setItem('refresh_token', mockResponse.refresh_token);
          localStorage.setItem('user', JSON.stringify(mockResponse.user));
          localStorage.setItem('session_id', mockResponse.session_id);
        } else {
          // TODO: Replace with actual API call using axiosInstance
          // const response = await axiosInstance.post(`${config.apiBaseUrl}/login`, {
          //   contact: contactInfo.value,
          //   password: password.value,
          //   loginMethod: 'password'
          // });
          // Handle actual response here
        }

        // Store SIP information
        localStorage.setItem('sipConnectionDetails', JSON.stringify({
          desc: 'SIP Connection Details',
          uri: sipConnectionDetails.value.uri,
          password: sipConnectionDetails.value.password,
          websocketURL: sipConnectionDetails.value.websocketURL
        }));

        // Store remember me preference
        if (rememberMe.value) {
          localStorage.setItem('rememberedContact', contactInfo.value);
          localStorage.setItem('rememberedMethod', loginMethod.value);
        } else {
          localStorage.removeItem('rememberedContact');
          localStorage.removeItem('rememberedMethod');
        }

        // Redirect to dashboard
        router.push(returnUrl.value);
      } catch (err) {
        error.value = 'Login failed. Please check your credentials.';
        console.error('Password login error:', err);
      } finally {
        loading.value = false;
      }
    };

    const requestOtp = async () => {
      loading.value = true;
      error.value = '';

      // Validate contact info
      if (!validateContactInfo()) {
        error.value = `Please enter a valid ${getContactLabel().toLowerCase()}`;
        loading.value = false;
        return;
      }

      try {
        if (config.enableMockApi) {
          // Mock API call - replace with actual axios call
          await new Promise(resolve => setTimeout(resolve, config.mockApiDelay));
          
          // Simulate successful OTP request
          userId.value = 'mock_user_id';
          maskedContact.value = maskContactInfo(contactInfo.value);
        } else {
          // TODO: Replace with actual API call using axiosInstance
          // const response = await axiosInstance.post(`${config.apiBaseUrl}/request-otp`, {
          //   contact: contactInfo.value,
          //   deliveryMethod: deliveryMethod.value
          // });
          // userId.value = response.data.userId;
          // maskedContact.value = response.data.maskedContact;
        }
        
        currentStep.value = 'otp';
        successMessage.value = `OTP sent successfully via ${deliveryMethod.value}!`;
        startResendTimer();

        setTimeout(() => {
          successMessage.value = '';
        }, config.successMessageDuration);
      } catch (err) {
        error.value = 'Failed to send OTP. Please try again.';
        console.error('OTP request error:', err);
      } finally {
        loading.value = false;
      }
    };

    const verifyOtp = async () => {
      loading.value = true;
      error.value = '';

      try {
        const otpCode = otpDigits.value.join('');
        
        if (config.enableMockApi) {
          // Mock API call - replace with actual axios call
          await new Promise(resolve => setTimeout(resolve, config.mockApiDelay));
          
          // Simulate successful verification
          const mockResponse = {
            access_token: 'mock_access_token',
            refresh_token: 'mock_refresh_token',
            user: { id: 1, name: 'Test User' },
            session_id: 'mock_session_id'
          };

          // Store authentication tokens and user data
          localStorage.setItem('access_token', mockResponse.access_token);
          localStorage.setItem('refresh_token', mockResponse.refresh_token);
          localStorage.setItem('user', JSON.stringify(mockResponse.user));
          localStorage.setItem('session_id', mockResponse.session_id);
        } else {
          // TODO: Replace with actual API call using axiosInstance
          // const response = await axiosInstance.post(`${config.apiBaseUrl}/verify-otp`, {
          //   userId: userId.value,
          //   otpCode: otpCode
          // });
          // Handle actual response here
        }

        // Store SIP information
        localStorage.setItem('sipConnectionDetails', JSON.stringify({
          desc: 'SIP Connection Details',
          uri: sipConnectionDetails.value.uri,
          password: sipConnectionDetails.value.password,
          websocketURL: sipConnectionDetails.value.websocketURL
        }));

        // Store remember me preference
        if (rememberMe.value) {
          localStorage.setItem('rememberedContact', contactInfo.value);
          localStorage.setItem('rememberedMethod', loginMethod.value);
        } else {
          localStorage.removeItem('rememberedContact');
          localStorage.removeItem('rememberedMethod');
        }

        // Redirect to dashboard
        router.push(returnUrl.value);
      } catch (err) {
        error.value = 'OTP verification failed. Please try again.';
        console.error('OTP verification error:', err);
      } finally {
        loading.value = false;
      }
    };

    const handleSubmit = async () => {
      submitted.value = true;

      if (!isFormValid.value) {
        return;
      }

      if (currentStep.value === 'email') {
        if (loginMethod.value === 'password') {
          await passwordLogin();
        } else if (loginMethod.value === 'otp') {
          await requestOtp();
        }
      } else if (currentStep.value === 'otp') {
        await verifyOtp();
      }
    };

    const resendOtp = async () => {
      loading.value = true;
      error.value = '';

      try {
        if (config.enableMockApi) {
          // Mock API call - replace with actual axios call
          await new Promise(resolve => setTimeout(resolve, config.mockApiDelay));
        } else {
          // TODO: Replace with actual API call using axiosInstance
          // await axiosInstance.post(`${config.apiBaseUrl}/resend-otp`, {
          //   userId: userId.value,
          //   deliveryMethod: deliveryMethod.value
          // });
        }

        successMessage.value = `OTP resent successfully via ${deliveryMethod.value}!`;
        startResendTimer();

        setTimeout(() => {
          successMessage.value = '';
        }, config.successMessageDuration);
      } catch (err) {
        error.value = 'Failed to resend OTP. Please try again.';
      } finally {
        loading.value = false;
      }
    };

    const goBackToEmail = () => {
      currentStep.value = 'email';
      otpDigits.value = ['', '', '', '', '', ''];
      submitted.value = false;
      error.value = '';
      successMessage.value = '';
      userId.value = '';

      if (resendInterval.value) {
        clearInterval(resendInterval.value);
        resendTimer.value = 0;
      }
    };

    const handleForgotPassword = () => {
      router.push('/forgot-password');
    };

    const handleHelp = () => {
      if (config.helpUrl) {
        window.open(config.helpUrl, '_blank');
      } else {
        console.log('Help clicked - Help URL not configured');
        // TODO: Implement help logic
      }
    };

    // Check for remembered data on component mount
    const checkRememberedData = () => {
      const rememberedContact = localStorage.getItem('rememberedContact');
      const rememberedMethod = localStorage.getItem('rememberedMethod');

      if (rememberedContact) {
        contactInfo.value = rememberedContact;
        rememberMe.value = true;
      }

      if (rememberedMethod) {
        loginMethod.value = rememberedMethod;
      }
    };

    // Lifecycle hooks
    onMounted(() => {
      checkRememberedData();

      try {
        if (config.sipCheckWebsocketUrl) {
          const checkWSConnection = new WebSocket(config.sipCheckWebsocketUrl, "sip");
          console.log("checking WebSocket Connection", checkWSConnection);
        }
      } catch (error) {
        console.log("WebSocket connection error:", error);
      }
    });

    onUnmounted(() => {
      if (resendInterval.value) {
        clearInterval(resendInterval.value);
      }
    });

    return {
      contactInfo,
      password,
      loginMethod,
      deliveryMethod,
      rememberMe,
      otpDigits,
      otpInputs,
      currentStep,
      loading,
      submitted,
      error,
      successMessage,
      maskedContact,
      resendTimer,
      showPassword,
      isOtpComplete,
      isFormValid,
      getContactLabel,
      getInputType,
      getInputPlaceholder,
      selectLoginMethod,
      handleDeliveryMethodChange,
      handleOtpInput,
      handleOtpKeydown,
      handleSubmit,
      resendOtp,
      goBackToEmail,
      handleForgotPassword,
      handleHelp,
      sipConnectionDetails,
      config, // Expose config if needed in template
    };
  }
};
</script>
<style>
@import url("@/styles/login.css");
</style>
