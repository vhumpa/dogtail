#!/usr/bin/env python3
from test_version import TestVersion
from test_utils import TestScreenshot, TestRun, TestDelay, TestA11Y, TestLock, TestI18N
from dogtail.logging import LOGGER
import dogtail


LOGGER.info("====================================")
LOGGER.info("Executiong tests for dogtail.version")
LOGGER.info("====================================")
run_test0 = TestVersion()

LOGGER.info("TestVersion.test_version_from_string_list()")
run_test0.test_version_from_string_list()
LOGGER.info("TestVersion.test_version_from_string()")
run_test0.test_version_from_string()
LOGGER.info("TestVersion.test_version_from_string_dedicated()")
run_test0.test_version_from_string_dedicated()
LOGGER.info("TestVersion.test_version_less_than()")
run_test0.test_version_less_than()
LOGGER.info("TestVersion.test_version_more_than()")
run_test0.test_version_more_than()
LOGGER.info("TestVersion.test_version_equals()")
run_test0.test_version_equals()


LOGGER.info("====================================")
LOGGER.info("Executiong tests for dogtail.utils")
LOGGER.info("====================================")
#run_test1_0 = TestScreenshot()
#run_test1_0.make_expected_and_compare("/tmp/dogtail-test-screenshot.jpg")
#run_test1_0.test_screenshot_incorrect_timestamp()
#run_test1_0.test_screenshot_default()
#run_test1_0.test_screenshot_basename()
#run_test1_0.test_screenshot_no_time_stamp()
#run_test1_0.test_screenshot_jpeg()
#run_test1_0.test_screenshot_unknown_format()
#run_test1_0.test_screenshot_incorrect_timestamp()
#run_test1_0.test_screenshot_incorrect_timestamp()
#run_test1_0.test_screenshot_incorrect_timestamp()

LOGGER.info("TestRun()")
run_test1_1 = TestRun()
LOGGER.info("TestRun().setUp")
run_test1_1.setUp()
LOGGER.info("TestRun().tearDown")
run_test1_1.tearDown()
LOGGER.info("TestRun().test_run")
run_test1_1.test_run()
LOGGER.info("TestRun().test_run_wrong")
run_test1_1.test_run_wrong()
LOGGER.info("TestRun().test_run_dumb")
run_test1_1.test_run_dumb()
import os
os.system("killall gtk3-demo")

LOGGER.info("TestDelay()")
run_test1_2 = TestDelay()
LOGGER.info("TestDelay().test_doDelay_implicit()")
run_test1_2.test_doDelay_implicit()
LOGGER.info("TestDelay().test_doDelay_explicit()")
run_test1_2.test_doDelay_explicit()
LOGGER.info("TestDelay().test_doDelay_logger()")
#run_test1_2.test_doDelay_logger()

LOGGER.info("TestA11Y()")
run_test1_3 = TestA11Y()
LOGGER.info("TestA11Y().test_bail_when_a11y_disabled()")
run_test1_3.test_bail_when_a11y_disabled()
LOGGER.info("TestA11Y().test_enable_a11y()")
run_test1_3.test_enable_a11y()

LOGGER.info("TestLock()")
run_test1_4 = TestLock()
LOGGER.info("TestLock().tearDown")
run_test1_4.tearDown()
LOGGER.info("TestLock().test_set_unrandomized_lock")
run_test1_4.test_set_unrandomized_lock()
LOGGER.info("TestLock().test_double_lock")
run_test1_4.test_double_lock()
dogtail.utils.Lock(lockname='dogtail-test.lock', randomize=False).unlock()
LOGGER.info("TestLock().test_double_unlock")
run_test1_4.test_double_unlock()
LOGGER.info("TestLock().test_randomize")
run_test1_4.test_randomize()

LOGGER.info("TestI18N()")
run_test1_5 = TestI18N()
LOGGER.info("TestI18N().test_load_all_translations_for_language")
run_test1_5.test_load_all_translations_for_language()


LOGGER.info("====================================")
LOGGER.info("Executiong tests for dogtail.tree")
LOGGER.info("====================================")
from test_tree import TestNode, TestSelection, TestValue, TestSearching, TestUnicodeNames, TestDump
list_of_tests = ["test_get_bogus","test_get_name","test_set_name","test_get_debugName",
"test_set_debugName","test_get_roleName","test_set_roleName","test_get_role","test_set_role",
"test_get_description","test_set_description","test_get_parent","test_set_parent",
"test_get_children","test_set_children","test_get_children_with_limit","test_get_combo_value",
"test_get_URI_not_implemented","test_set_text","test_text_set_error","test_caretOffset",
"test_comboValue","test_getStateSet","test_setStateSet","test_get_relations","test_get_labelee",
"test_set_labelee","test_get_labeler","test_set_labeller","test_get_sensitive","test_set_sensitive",
"test_get_showing","test_set_showing","test_get_visible","test_set_visible","test_get_actions",
"test_set_actions","test_get_extents","test_get_extens_wrong","test_set_extents","test_get_position",
"test_get_position_not_implemented","test_set_position","test_get_size_not_implemented",
"test_set_size","test_get_toolkit","test_set_toolkit","test_get_ID","test_set_ID","test_checked",
"test_dead","test_contains","test_childAtPoint","test_click","test_doubleClick","test_point",
"test_typeText_nonfucable"]
LOGGER.info("TestNode()")
for test in list_of_tests:
    LOGGER.info("TestNode().%s" % test)
    testing = TestNode()
    testing.setUp()
    getattr(testing, test)()
    testing.tearDown()


list_of_tests = ["test_tabs", "test_iconView"]
LOGGER.info("TestSelection()")
for test in list_of_tests:
    LOGGER.info("TestSelection().%s" % test)
    testing = TestSelection()
    testing.setUp()
    getattr(testing, test)()
    testing.tearDown()

list_of_tests = ["test_get_value", "test_set_value", "test_min_value", "test_max_value", "test_min_value_increment"]
LOGGER.info("TestValue()")
for test in list_of_tests:
    LOGGER.info("TestValue().%s" % test)
    testing = TestValue()
    testing.setUp()
    getattr(testing, test)()
    testing.tearDown()


list_of_tests = ["test_findChildren", "test_findChild_lambda", "test_findChildren2", 
"test_findChildren2_lambda", "test_findChildren_lambdas", "test_findAncestor", "test_isChild", 
"test_getUserVisibleStrings", "test_satisfies", "test_absoluteSearchPath", 
"test_compare_equal_search_paths", "test_compare_unequal_search_paths_different_length", 
"test_compare_unequal_search_paths_same_length", "test_get_search_path_length", 
"test_iterate_search_path", "test_make_script_method_call_from_search_path", 
"test_get_relative_search_path_for_path", "test_get_prefix_for_search_path", "test_get_predicate", 
"test_getRelativeSearch_app", "test_getRelativeSearch_widget", "test_findChildren_non_recursive", 
"test_find_by_shortcut", "test_find_by_shortcut2"]
LOGGER.info("TestSearching()")
for test in list_of_tests:
    LOGGER.info("TestSearching().%s" % test)
    testing = TestSearching()
    testing.setUp()
    getattr(testing, test)()
    testing.tearDown()


list_of_tests = ["setUp", "test_unicode_char_in_name", "test_unicode_char_in_name_click", 
"test_unicode_logging_nocrash", "tearDown"]
LOGGER.info("TestUnicodeNames()")
for test in list_of_tests:
    LOGGER.info("TestUnicodeNames().%s" % test)
    testing = TestUnicodeNames()
    testing.setUp()
    getattr(testing, test)()
    testing.tearDown()


list_of_tests = ["test_dump_to_stdout", "test_dump_with_actions"]
LOGGER.info("TestDump()")
for test in list_of_tests:
    LOGGER.info("TestDump().%s" % test)
    testing = TestDump()
    testing.setUp()
    getattr(testing, test)()
    testing.tearDown()


LOGGER.info("====================================")
LOGGER.info("Executiong tests for dogtail.rawinput")
LOGGER.info("====================================")
from test_rawinput import TestRawinput
list_of_tests = ["test_motion", "test_motion_with_trajectory",
"test_check_coordinates_direct", "test_check_coordinates_builtin",
"test_doubleClick", "test_click", "test_press_release", "test_drag",
"test_drag_with_trajectory", "test_pressKey_no_such_key", "test_keyCombo_simple",
"test_keyCombo_multi", "test_keyCombo_wrong_key", "test_typeText"]
LOGGER.info("TestRawinput()")
for test in list_of_tests:
    LOGGER.info("TestRawinput().%s" % test)
    testing = TestRawinput()
    testing.setUp()
    getattr(testing, test)()
    testing.tearDown()

import os
os.system("killall gtk3-demo")
LOGGER.info("====================================")
LOGGER.info("Executiong tests for dogtail.procedural")
LOGGER.info("====================================")
from test_procedural import TestFocusApplication, TestFocusWindow, TestFocusDialog, TestFocusWidget, TestFocus, TestKeyCombo, TestActions
list_of_tests = ["test_throw_exception_on_focusing_bogus_name",
                 "test_focusing_basic",
                 "test_throw_exception_on_get_no_such_attribute",
                 "test_throw_exception_on_get_no_such_attribute_when_node_doesnt_exist",
                 "test_throw_exception_on_set_no_such_attribute"]

LOGGER.info("TestFocusApplication()")
for test in list_of_tests:
    LOGGER.info("TestFocusApplication().%s" % test)
    testing = TestFocusApplication()
    testing.setUp()
    getattr(testing, test)()
    testing.tearDown()


list_of_tests = ["test_focusing_bogus_name_without_a_fatal_error",
                 "test_throw_exception_on_focusing_bogus_name"]
LOGGER.info("TestFocusWindow()")
for test in list_of_tests:
    LOGGER.info("TestFocusWindow().%s" % test)
    testing = TestFocusWindow()
    testing.setUp()
    getattr(testing, test)()
    testing.tearDown()


list_of_tests = ["test_focusing_bogus_name_without_a_fatal_error",
                 "test_throw_exception_on_focusing_bogus_name"]
LOGGER.info("TestFocusDialog()")
for test in list_of_tests:
    LOGGER.info("TestFocusDialog().%s" % test)
    testing = TestFocusDialog()
    testing.setUp()
    getattr(testing, test)()
    testing.tearDown()


list_of_tests = ["test_focusing_empty_name",
                 "test_focusing_bogus_name_without_a_fatal_error",
                 "test_throw_exception_on_focusing_bogus_name",
                 "test_focusing_basic"]
LOGGER.info("TestFocusWidget()")
for test in list_of_tests:
    LOGGER.info("TestFocusWidget().%s" % test)
    testing = TestFocusWidget()
    testing.setUp()
    getattr(testing, test)()
    testing.tearDown()


list_of_tests = ["test_initial_state",
                 "test_focusing_app",
                 "test_focusing_app_via_application",
                 "test_focus_getting_bogus_attribute",
                 "test_focus_setting_bogus_attribute",
                 "test_focusing_roleName",
                 "test_focus_menu",
                 "test_focus_menuItem",
                 "test_focus_button",
                 "test_focus_table",
                 "test_focus_tableCell",
                 "test_focus_text",
                 "test_focus_icon"]
LOGGER.info("TestFocus()")
for test in list_of_tests:
    LOGGER.info("TestFocus().%s" % test)
    testing = TestFocus()
    testing.setUp()
    getattr(testing, test)()
    testing.tearDown()


list_of_tests = ["test_keyCombo",
                 "test_keyCombo_on_widget"]
LOGGER.info("TestKeyCombo()")
for test in list_of_tests:
    LOGGER.info("TestKeyCombo().%s" % test)
    testing = TestKeyCombo()
    testing.setUp()
    getattr(testing, test)()
    testing.tearDown()

#from test_procedural import TestFocusApplication, TestFocusWindow, TestFocusDialog, TestFocusWidget, TestFocus, TestKeyCombo, TestActions

list_of_tests = ["test_click",
                 "test_click_on_invisible_element",
                 "test_click_with_raw",
                 "test_select",
                 "test_deselect",
                 "test_typing_on_widget",
                 "test_custom_actions",
                 "test_blink_on_actions",
                 "test_custom_actions_button",
                 "test_custom_actions_menu",
                 "test_custom_actions_text",
                 "test_custom_actions_table_cell",
                 "test_throws_action_not_supported",
                 "test_action_on_insensitive"]
LOGGER.info("TestActions()")
for test in list_of_tests:
    LOGGER.info("TestActions().%s" % test)
    testing = TestActions()
    testing.setUp()
    getattr(testing, test)()
    testing.tearDown()


LOGGER.info("====================================")
LOGGER.info("Executiong tests for dogtail.predicate")
LOGGER.info("====================================")
from test_predicate import TestPredicate
list_of_tests = ["test_capitalization",
                 "test_abstract_class",
                 "test_correct_equality",
                 "test_incorrect_equality",
                 "test_predicates_application",
                 "test_predicates_window",
                 "test_predicates_window_named",
                 "test_predicates_menu_named",
                 "test_predicates_menu_item_named",
                 "test_predicates_text_entry_named",
                 "test_predicates_button_named",
                 "test_predicates_page_tab_named",
                 "test_predicates_generic_by_name",
                 "test_predicates_generic_by_roleName",
                 "test_predicates_generic_by_description",
                 "test_predicates_generic_by_label",
                 "test_predicates_named",
                 "test_predicates_labelled_as",
                 "test_predicates_dialog_named"]

LOGGER.info("TestPredicate()")
for test in list_of_tests:
    LOGGER.info("TestPredicate().%s" % test)
    testing = TestPredicate()
    getattr(testing, test)()


LOGGER.info("====================================")
LOGGER.info("Executiong tests for dogtail.config")
LOGGER.info("====================================")
from test_config import TestConfiguration
list_of_tests = ["test_get_set_all_properties",
                 "test_default_directories_created",
                 "test_set",
                 "test_get",
                 "test_create_scratch_directory",
                 "test_create_data_directory",
                 "test_create_log_directory",
                 "test_load",
                 "test_reset"]

LOGGER.info("TestConfiguration()")
for test in list_of_tests:
    LOGGER.info("TestConfiguration().%s" % test)
    testing = TestConfiguration()
    getattr(testing, test)()


LOGGER.info("====================================")
LOGGER.info("Executiong tests for dogtail.logging")
LOGGER.info("====================================")
from test_logging import TestLogging
list_of_tests = ["test_entryStamp_is_not_empty",
                 "test_unique_name",
                 "test_no_new_line_to_file",
                 "test_no_new_line_to_stdout",
                 "test_no_new_line_to_both_file_and_stdout",
                 "test_force_to_file",
                 "test_results_logger_correct_dict",
                 "test_results_logger_incorrect_dict",
                 "test_correct_error_if_log_dir_does_not_exist"]

LOGGER.info("TestLogging()")
for test in list_of_tests:
    LOGGER.info("TestLogging().%s" % test)
    testing = TestLogging()
    testing.setUp()
    getattr(testing, test)()
    testing.tearDown()

os.system("killall gtk3-demo")
print("exiting with 0")
exit(0)
