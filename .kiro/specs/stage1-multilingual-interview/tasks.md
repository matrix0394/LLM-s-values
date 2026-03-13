# Implementation Plan

- [ ] 1. Create LLMMultilingualInterview class




  - [x] 1.1 Create new file `src/llm_values/llm_multilingual_interview.py` with class skeleton






    - Inherit from BaseInterview
    - Define UN_LANGUAGE_SYSTEM_PROMPTS dictionary with all 6 language translations
    - Initialize multilingual questions configuration loader
    - _Requirements: 1.1, 1.3_

  - [ ] 1.2 Write property test for language configuration completeness








    - **Property 1: Language Configuration Completeness**
    - **Validates: Requirements 1.1, 2.2**
  - [x] 1.3 Implement `get_un_official_languages()` method


    - Return list of 6 UN official language codes: ['en', 'fr', 'es', 'ru', 'ar', 'zh-cn']
    - _Requirements: 1.1_
  - [x] 1.4 Implement `_load_multilingual_questions()` method


    - Load questions from `config/multilingual_questions_complete.json`
    - Filter to only include UN official languages
    - _Requirements: 1.1, 1.2_

  - [ ] 1.5 Write property test for question text language consistency







    - **Property 2: Question Text Language Consistency**
    - **Validates: Requirements 1.2**


- [ ] 2. Implement single language interview functionality


  - [x] 2.1 Implement `interview_single_language(model_name, language)` method


    - Get questions for the specified language
    - Use language-appropriate system prompt
    - Call `ask_question_with_retry` for each question
    - Return structured result with language identifier
    - _Requirements: 1.2, 1.3, 1.4_
  - [ ]* 2.2 Write property test for system prompt language appropriateness
    - **Property 3: System Prompt Language Appropriateness**
    - **Validates: Requirements 1.3**

  - [-] 2.3 Implement `_single_round_multilingual_interview(model_name, language)` method

    - Execute one complete questionnaire round
    - Return responses with timing and validity info
    - _Requirements: 1.2_
  - [ ]* 2.4 Write property test for result language identification
    - **Property 4: Result Language Identification**
    - **Validates: Requirements 1.4**

- [ ] 3. Implement consensus mechanism for multilingual interviews
  - [x] 3.1 Implement `_multi_round_multilingual_interview(model_name, language)` method

    - Execute consensus_count rounds of complete questionnaire
    - Calculate mode for each question across rounds
    - Compute confidence (consistency rate) for each question
    - _Requirements: 3.1, 3.2, 3.3_
  - [ ]* 3.2 Write property test for consensus round count
    - **Property 7: Consensus Round Count**
    - **Validates: Requirements 3.1**
  - [ ]* 3.3 Write property test for mode calculation with confidence
    - **Property 8: Mode Calculation with Confidence**
    - **Validates: Requirements 3.2, 3.3**
  - [x] 3.4 Implement intermediate data storage in results

    - Include all_rounds data in result
    - Include consistency_stats for each question
    - _Requirements: 3.4_
  - [ ]* 3.5 Write property test for result data completeness
    - **Property 9: Result Data Completeness**
    - **Validates: Requirements 3.4**

- [ ] 4. Checkpoint - Make sure all tests are passing
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Implement batch multilingual interview functionality
  - [x] 5.1 Implement `interview_model_multilingual(model_name)` method

    - Iterate through all 6 UN official languages
    - Call interview_single_language for each language
    - Aggregate results by language
    - _Requirements: 2.2_

  - [ ] 5.2 Implement `batch_multilingual_interview(model_names, languages, skip_existing)` method
    - Iterate through all specified models
    - Support skip_existing flag for incremental interviews
    - Save individual results after each model-language completion
    - _Requirements: 2.1, 2.2, 5.1, 5.2_
  - [ ]* 5.3 Write property test for skip existing correctness
    - **Property 13: Skip Existing Correctness**
    - **Validates: Requirements 5.1, 5.2**

- [x] 6. Implement incremental save and resume functionality

  - [ ] 6.1 Implement `save_individual_result(model_name, language, result)` method
    - Save to `data/llm_values/interview_raw/` directory
    - Use timestamped filename: `{model}_{language}_{timestamp}.json/pkl`
    - Save both JSON and pickle formats
    - _Requirements: 2.4, 5.4_
  - [ ]* 6.2 Write property test for incremental save with timestamps
    - **Property 6: Incremental Save with Timestamps**
    - **Validates: Requirements 2.4, 5.4**
  - [x] 6.3 Implement `_load_existing_multilingual_data(data_dir)` method

    - Scan for existing model-language combination files
    - Return set of completed combinations
    - _Requirements: 5.1_

  - [x] 6.4 Implement `_merge_multilingual_results(existing, new)` method





    - Merge new results with existing data
    - Ensure no duplicates
    - _Requirements: 5.3_
  - [x] 6.5 Write property test for merge without duplicates






    - **Property 14: Merge Without Duplicates**
    - **Validates: Requirements 5.3**


- [x] 7. Checkpoint - Make sure all tests are passing




  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Implement retry mechanism





  - [x] 8.1 Verify retry behavior in `ask_question_with_retry` from BaseInterview


    - Ensure max_retry parameter is respected
    - Verify exponential backoff for rate limits
    - _Requirements: 2.3_
  - [ ]* 8.2 Write property test for retry behavior correctness
    - **Property 5: Retry Behavior Correctness**
    - **Validates: Requirements 2.3**

- [ ] 9. Implement data processing and analysis





  - [x] 9.1 Create `LLMMultilingualDataProcessor` class in `src/llm_values/llm_multilingual_data_processor.py`


    - Implement `load_raw_results()` method
    - Implement `convert_to_ivs_format()` method
    - Implement `generate_entity_id(model, language)` method
    - _Requirements: 4.1_
  - [ ]* 9.2 Write property test for IVS format conversion
    - **Property 10: IVS Format Conversion**
    - **Validates: Requirements 4.1**
  - [x] 9.3 Implement PCA analysis integration


    - Use existing `LLMPCAAnalysis` class
    - Generate cultural coordinates for each model-language combination
    - _Requirements: 4.2_
  - [ ]* 9.4 Write property test for PCA output dimensions
    - **Property 11: PCA Output Dimensions**
    - **Validates: Requirements 4.2**

  - [x] 9.5 Implement `save_processed_results()` method

    - Save both JSON and pickle formats
    - _Requirements: 4.3_
  - [ ]* 9.6 Write property test for dual format output
    - **Property 12: Dual Format Output**
    - **Validates: Requirements 4.3**
  - [x] 9.7 Implement summary report generation


    - Generate comparison report across languages for each model
    - _Requirements: 4.4_

- [ ] 10. Checkpoint - Make sure all tests are passing






  - Ensure all tests pass, ask the user if questions arise.

- [x] 11. Create run script and integration





  - [x] 11.1 Create `src/run/run_llm_multilingual_analysis.py` script


    - Import LLMMultilingualInterview and LLMMultilingualDataProcessor
    - Implement main() function with command line options
    - Support --models, --languages, --skip-existing flags
    - _Requirements: 2.1, 5.1_
  - [x] 11.2 Add integration with existing analysis pipeline


    - Ensure output is compatible with existing visualization tools
    - _Requirements: 4.2, 4.3_

- [x] 12. Final Checkpoint - Make sure all tests are passing





  - Ensure all tests pass, ask the user if questions arise.
