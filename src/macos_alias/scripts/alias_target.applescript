#!/usr/bin/osascript
-- list_alias: Show the target of a MacOS alias
-- TODO Create functions that can be called from Python

on run argv
    -- Check that one argument was passed
    if (count of argv) = 1 then
        -- Check the first argument; expand it
        set alias_path to item 1 of argv
        try
            set expanded_alias_path to do shell script "echo " & quoted form of alias_path & " | tr '\\n' '\\0' | xargs -0 realpath"
        on error errorMessage number errorNumber
            if errorNumber = 1 then
                return "Error: " & alias_path & " does not exist"
            else
                return "Error: " & errorMessage
            end if
 -- Most likely, the alias file does not exist
            return "Error #" & errorNumber & ": " & errorMessage
        end try
        set test_file to POSIX file expanded_alias_path
        tell application "Finder"
            set is_alias to (class of item test_file is alias file)
        end tell
        if not is_alias then
            return alias_path & " is not an alias"
        end if

        try
            tell application "Finder"
                set this_path to POSIX file expanded_alias_path as text
                set original_file to original item of file this_path
            end tell
        on error errorMessage number errorNumber
            if errorNumber = -1728 then -- Broken alias
                return alias_path & " is a broken alias"
            else
                return "Error# " & errorNumber & ": " & errorMessage
            end if
        end try
        try
            tell application "Finder"
                set original_file_text to original_file as text
                set alias_name to POSIX path of original_file_text
            end tell
--        try
--            tell application "Finder" to set alias_name to POSIX path of ((original item of file (POSIX file expanded_alias_path as text)) as text)
        on error errorMessage number errorNumber
            if errorNumber = -1700 then -- Broken alias
                return alias_path & " is a broken alias"
            else
                return "Error: " & errorMessage
            end if
        end try
        return alias_path & " is an alias of " & alias_name
    else
        return "Usage: alias_target <alias_file>"
    end if
end run
