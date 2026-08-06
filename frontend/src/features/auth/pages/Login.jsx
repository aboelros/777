import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Mail, Lock, Sparkles, ArrowRight, Loader2, AlertCircle, Shield, Eye, EyeOff } from 'lucide-react';
import { useAuthStore } from '../../../store/authStore';

export default function Login() {
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [focusedField, setFocusedField] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const result = await login(email, password);
      if (result.success) {
        navigate('/');
      } else {
        setError(result.error || 'Invalid credentials');
      }
    } catch (err) {
      setError(err.message || 'An unexpected error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 bg-[rgb(2,6,23)]">
        {/* Ambient Grid */}
        <div
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `linear-gradient(rgba(14,165,233,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(14,165,233,0.3) 1px, transparent 1px)`,
            backgroundSize: '60px 60px',
          }}
        />
        {/* Neon Orbs */}
        <motion.div
          className="absolute top-1/4 left-1/5 w-[500px] h-[500px] bg-sky-500/8 rounded-full blur-[120px]"
          animate={{
            scale: [1, 1.15, 1],
            opacity: [0.4, 0.6, 0.4],
            x: [0, 30, 0],
            y: [0, -20, 0],
          }}
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          className="absolute bottom-1/4 right-1/5 w-[400px] h-[400px] bg-cyan-500/8 rounded-full blur-[100px]"
          animate={{
            scale: [1.1, 1, 1.1],
            opacity: [0.5, 0.3, 0.5],
            x: [0, -25, 0],
            y: [0, 20, 0],
          }}
          transition={{ duration: 12, repeat: Infinity, ease: "easeInOut" }}
        />
        {/* Top accent line */}
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-sky-500/30 to-transparent" />
      </div>

      {/* Login Card */}
      <motion.div
        initial={{ opacity: 0, y: 30, scale: 0.97 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.7, ease: [0.25, 0.46, 0.45, 0.94] }}
        className="relative z-10 w-full max-w-md"
      >
        {/* Glass Card Container */}
        <div className="bg-slate-950/60 backdrop-blur-2xl rounded-3xl border border-white/[0.08] shadow-2xl shadow-black/50 overflow-hidden">
          {/* Animated top border glow */}
          <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-sky-400/40 to-transparent" />

          {/* Header Section */}
          <div className="p-8 pb-6 text-center">
            {/* Logo */}
            <motion.div
              initial={{ scale: 0.5, opacity: 0, rotate: -10 }}
              animate={{ scale: 1, opacity: 1, rotate: 0 }}
              transition={{ delay: 0.2, duration: 0.6, type: "spring", stiffness: 200 }}
              className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-sky-500/15 to-cyan-500/10 border border-sky-500/20 mb-6 relative"
            >
              <div className="absolute inset-0 rounded-2xl bg-sky-500/5 animate-pulse" />
              <Sparkles className="w-10 h-10 text-sky-400 relative z-10 drop-shadow-[0_0_12px_rgba(14,165,233,0.5)]" />
            </motion.div>

            {/* Title */}
            <motion.h1
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.5 }}
              className="text-3xl font-bold text-white mb-2 tracking-tight"
            >
              Welcome Back
            </motion.h1>
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
              className="text-slate-400 text-sm tracking-wide"
            >
              Sign in to your command center
            </motion.p>
          </div>

          {/* Form Section */}
          <div className="px-8 pb-8">
            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Error Message */}
              <AnimatePresence>
                {error && (
                  <motion.div
                    initial={{ opacity: 0, y: -10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -10, scale: 0.95 }}
                    className="p-4 rounded-2xl bg-red-500/8 border border-red-500/15 flex items-center gap-3"
                  >
                    <div className="w-8 h-8 rounded-lg bg-red-500/15 flex items-center justify-center flex-shrink-0">
                      <AlertCircle className="w-4 h-4 text-red-400" />
                    </div>
                    <p className="text-sm text-red-400">{error}</p>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Email Input */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 }}
                className="space-y-2"
              >
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-widest pl-1">
                  Email
                </label>
                <div className="relative group">
                  <div className={`absolute left-4 top-1/2 -translate-y-1/2 transition-colors duration-300 ${focusedField === 'email' ? 'text-sky-400' : 'text-slate-500'}`}>
                    <Mail className="w-5 h-5" />
                  </div>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    onFocus={() => setFocusedField('email')}
                    onBlur={() => setFocusedField(null)}
                    required
                    className="w-full pl-12 pr-4 py-4 bg-white/[0.03] border border-white/[0.08] rounded-2xl text-white placeholder-slate-600 focus:outline-none focus:bg-white/[0.05] focus:border-sky-500/40 focus:shadow-[0_0_0_3px_rgba(14,165,233,0.08)] transition-all duration-300"
                    placeholder="you@example.com"
                  />
                </div>
              </motion.div>

              {/* Password Input */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 }}
                className="space-y-2"
              >
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-widest pl-1">
                  Password
                </label>
                <div className="relative group">
                  <div className={`absolute left-4 top-1/2 -translate-y-1/2 transition-colors duration-300 ${focusedField === 'password' ? 'text-sky-400' : 'text-slate-500'}`}>
                    <Lock className="w-5 h-5" />
                  </div>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    onFocus={() => setFocusedField('password')}
                    onBlur={() => setFocusedField(null)}
                    required
                    className="w-full pl-12 pr-12 py-4 bg-white/[0.03] border border-white/[0.08] rounded-2xl text-white placeholder-slate-600 focus:outline-none focus:bg-white/[0.05] focus:border-sky-500/40 focus:shadow-[0_0_0_3px_rgba(14,165,233,0.08)] transition-all duration-300"
                    placeholder="••••••••••••"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 hover:text-sky-400 transition-colors"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </motion.div>

              {/* Submit Button */}
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.7 }}
              >
                <motion.button
                  type="submit"
                  disabled={isLoading}
                  whileHover={{ scale: 1.015, boxShadow: '0 0 30px rgba(14,165,233,0.3)' }}
                  whileTap={{ scale: 0.98 }}
                  className="w-full py-4 px-6 bg-gradient-to-r from-sky-500 to-cyan-500 hover:from-sky-400 hover:to-cyan-400 text-white font-semibold rounded-2xl shadow-lg shadow-sky-500/20 transition-all duration-300 flex items-center justify-center gap-2.5 disabled:opacity-50 disabled:cursor-not-allowed relative overflow-hidden group"
                >
                  {/* Button shine */}
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700" />
                  {isLoading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      <span>Signing In...</span>
                    </>
                  ) : (
                    <>
                      <span>Sign In</span>
                      <ArrowRight className="w-5 h-5 group-hover:translate-x-0.5 transition-transform" />
                    </>
                  )}
                </motion.button>
              </motion.div>
            </form>
          </div>

          {/* Footer */}
          <div className="px-8 py-5 bg-white/[0.02] border-t border-white/[0.05]">
            <div className="flex items-center justify-center gap-2 text-xs text-slate-500">
              <Shield className="w-3.5 h-3.5" />
              <span className="uppercase tracking-[0.15em] font-medium">Protected by Enterprise Security</span>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
