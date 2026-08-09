#!/usr/bin/osascript
-- is_alias: Test whether a file is a macOS Finder alias

on run argv
    -- Check that one arguments was passed
    if (count of argv) = 1 then
        -- Check the first argument; expand it
        set alias_path to item 1 of argv
        try
            set expanded_alias_path to do shell script "echo " & quoted form of alias_path & " | xargs realpath"
        on error errorMessage number errorNumber -- Most likely, the file does not exist
            error errorMessage number 1
        end try
        set test_file to POSIX file expanded_alias_path
        tell application "Finder"
            if exists test_file then
                set is_alias to (class of item test_file is alias file)
            else
                return alias_path & "does not exist"
            end if
            if is_alias then
                return alias_path & " is an alias"
            else
                return alias_path & " is not an alias"
            end if
        end tell
    else
        return "Usage: is_alias file"
    end if
end run
