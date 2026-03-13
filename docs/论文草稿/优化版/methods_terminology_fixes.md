# Methods Terminology and Style Fixes

## Additional Corrections Applied (Round 2)

### B. Terminology Consistency Issues

#### ✅ 11. Unified Language Terminology
**Problem**: Mixed use of "native language", "official language", "English-native countries"

**Changes Made**:
- Changed "non–English-native countries" → "non–English-speaking countries"
- Changed "English-native countries" → "English-speaking countries where English is a primary official language"
- Changed "native-language prompting" → "official-language prompting"
- Changed "native language" → "official language" in analysis descriptions

**Added Clarification**:
"Countries are included in language comparison analyses only when both English and non-English official language data are available; countries with English as the sole evaluation language form a separate English-only group."

**Rationale**: 
- Avoids confusion between "native speaker" and "official language"
- Clarifies that n=21 refers to countries using English for evaluation, not cultural "Anglosphere"
- Aligns with Study 4c's discussion of data limitations

---

#### ✅ 12. Study 4c Data Limitation Alignment with Study 2
**Problem**: Study 4c mentions African countries lacking native language data, but Study 2 says all non-English countries have language comparisons

**Fix**: Added explicit statement in Study 2:
"Countries are included in language comparison analyses only when both English and non-English official language data are available; countries with English as the sole evaluation language form a separate English-only group."

**Rationale**: Makes it clear that not all 66 countries have language comparisons, preventing contradiction with Study 4c.

---

#### ✅ 13. Language Family Classification (Altaic Controversy)
**Problem**: "Altaic (Turkish, Japanese, Korean)" is linguistically controversial

**Changes Made**:
- Removed "Altaic"
- Changed to: "Turkic (Turkish), Japonic (Japanese), and Koreanic (Korean)"

**Rationale**: 
- Avoids unnecessary reviewer controversy
- Uses accepted, non-controversial language family classifications
- More precise and defensible

---

### C. Results-Style Statements Removed from Methods

#### ✅ 14. Removed Specific Cohen's d Values from Robustness Section
**Before**: "Cohen's d = 1.38 for large models vs d = 1.43 for all models"

**After**: "Results remain consistent across model size categories (details in SI Appendix)."

**Rationale**: 
- Specific numerical results belong in Results/SI, not Methods
- Prevents inconsistency if results are updated
- Methods should describe procedures, not report findings

---

#### ✅ 15. Removed Directional Result Statements
**Before**: "Chinese models show weaker English advantages for Chinese-language contexts"

**After**: "Results are reported by model origin in SI Appendix."

**Rationale**:
- Directional conclusions belong in Results, not Methods
- Methods should describe what analyses were done, not what was found
- Prevents Methods-Results conflicts

---

## Summary of All Terminology Changes

### Consistent Terminology Now Used:

| Old Term | New Term | Context |
|----------|----------|---------|
| Native language | Official language | Throughout Study 2 |
| English-native countries | English-speaking countries | Study 2 Design |
| Non–English-native | Non–English-speaking | Study 2 Analysis |
| Native-language prompting | Official-language prompting | Study 2 Analysis |
| Altaic (Turkish, Japanese, Korean) | Turkic (Turkish), Japonic (Japanese), Koreanic (Korean) | Study 2 Design |

### Results Statements Removed:

1. Specific Cohen's d values (1.38 vs 1.43) → "Results remain consistent"
2. "Chinese models show weaker English advantages" → "Results reported by model origin in SI"
3. Directional pattern descriptions → Moved to Results section

---

## Files Updated

1. ✅ `docs/论文草稿/优化版/paper_pnas_methods_v2.md` (English)
2. ✅ `docs/论文草稿/优化版/paper_pnas_methods_v2_CN.md` (Chinese)

---

## Impact Assessment

### High Impact (Prevents Reviewer Confusion)
- Unified language terminology (native vs official)
- Study 2/4c data limitation alignment
- Removed Altaic classification

### Medium Impact (Improves Methods-Results Separation)
- Removed specific Cohen's d values
- Removed directional result statements

---

## Verification Checklist

- [x] Consistent use of "official language" vs "native language"
- [x] Clear definition of English-speaking vs non-English-speaking countries
- [x] Study 2 sample description aligns with Study 4c data limitations
- [x] Removed controversial "Altaic" language family
- [x] Removed all specific numerical results from Methods
- [x] Removed all directional conclusions from Methods
- [x] All changes applied to both English and Chinese versions

---

## Combined with Previous Fixes

**Total corrections made across both rounds**:
- 10 data errors fixed (Round 1)
- 5 terminology/style issues fixed (Round 2)
- **15 total corrections applied**

All Methods sections now follow proper scientific writing conventions:
- Methods describe procedures, not results
- Terminology is consistent and defensible
- No contradictions between different study sections
- Clear separation between Methods and Results
