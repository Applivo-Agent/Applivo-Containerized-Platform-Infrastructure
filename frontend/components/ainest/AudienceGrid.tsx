"use client";

import { motion } from "framer-motion";

const groups = [
  {
    title: "For job seekers",
    description: "Create production-quality resumes with unprecedented speed and ATS style-consistency."
  },
  {
    title: "For students",
    description: "Bring your best career ideas to life at scale, with an intuitive AI suite designed for applying."
  },
  {
    title: "For professionals",
    description: "Experience automated job applying and market tracking with unmatched scalability."
  }
];

export function AudienceGrid() {
  return (
    <section className="bg-[#050505] py-24 px-6 relative z-10 border-b border-zinc-900/50">
      <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-12 md:gap-8">
        {groups.map((group, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6, delay: i * 0.15 }}
            className="flex flex-col gap-3"
          >
            <h3 className="text-xl font-medium text-white tracking-tight">{group.title}</h3>
            <p className="text-[#a1a1aa] leading-relaxed text-[15px]">{group.description}</p>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
