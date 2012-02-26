#!/usr/bin/perl

use strict;
use warnings;
use English qw(-no_match_vars);

my $DICTIONARY_HOME = "/opt/rudder/share/upgrade-tools";
# Dictionaries
my $DICTIONARY_ATTRIBUTES = "$DICTIONARY_HOME/rudder-upgrade-LDAP-schema-2.3-2.4-PI-PT-CR-names-changed-attribute-map.csv";
my $DICTIONARY_OBJECTCLASSES = "$DICTIONARY_HOME/rudder-upgrade-LDAP-schema-2.3-2.4-PI-PT-CR-names-changed-objectclass-map.csv";
my $DICTIONARY_BRANCHES = "$DICTIONARY_HOME/rudder-upgrade-LDAP-schema-2.3-2.4-PI-PT-CR-names-changed-branches-map.csv";
my (%attributeDict, %objectClassDict, %branchDict);

# Function to display usage
sub usage {
	print "Usage: $PROGRAM_NAME LDIF-file\n";
}

# This script should only have one argument
if ( @ARGV != 1 ) {
	usage;
	exit 1;
}

if ( $UID != 0 ) {
	print "This command must be run as root!\n";
	exit 2;
}

# This script takes a LDIF file to modify as an argument
my $LDIF_FILENAME = $ARGV[0];

# Function to read a CSV file (first argument)
# and populate a hash
sub readDictionary {
	my($dictionaryFilename, $dictionary) = @_;

	open DICT_FH, $dictionaryFilename or die "Can't open dictionary '$dictionaryFilename': $!";
	while (<DICT_FH>) {
		next if ( /^#/ or /^\s*$/ );
		(my $key, my $value, undef, my $value2) = /([^;]+); *([^;]+)(; *([^;]+))?\n$/;
		${$dictionary}{lc "$key"} = $value;

		# Special case for the branch dictionary - the CSV file has a third column with the full entry in
		if ( defined $value2 ) {
			$value2 =~ s/\\n/\n/g;
			${$dictionary}{lc "$key-fullentry"} = $value2;
		}
	}
	close DICT_FH;
}


# Function to apply any replacements on a attribute/DN line
sub replaceNames {
	my ($line) = @_;

	if ( $line =~ /^dn: / ) {
		foreach my $dnAttribute (keys %attributeDict) {
			$line =~ s/$dnAttribute=/$attributeDict{lc $dnAttribute}=/ig;
		}
	} elsif ( $line =~ /^(objectClass|structuralObjectClass): / ) {
		(my $objectClassAttrName, my $objectClassName) = $line =~ /(objectClass|structuralObjectClass): (.*)$/;

		if ( defined $objectClassDict{lc $objectClassName} ) {
			print RES_FILE "$objectClassAttrName: $objectClassDict{lc $objectClassName}\n";
			return;
		}
	} else {
		(my $attrName, my $value) = $line =~ /([a-zA-Z]+)::? (.*)$/;

		if ( defined $attributeDict{lc $attrName} ) {
			print RES_FILE "$attributeDict{lc $attrName}: $value\n";
			return;
		}
	}

	# Print line
	print RES_FILE $line;
}


# Import dictionaries
readDictionary($DICTIONARY_ATTRIBUTES, \%attributeDict);
readDictionary($DICTIONARY_OBJECTCLASSES, \%objectClassDict);
readDictionary($DICTIONARY_BRANCHES, \%branchDict);


# Open temporary output file
open(RES_FILE, ">", $LDIF_FILENAME . ".tmp") or die("Error opening temporary file to write: $!");

# Open input file
open(LDIF_FILE, $LDIF_FILENAME) or die "Can't open LDIF file '$LDIF_FILENAME': $!";

# We need to recognize 4 cases in this file:
# 1) Attributes to rename (s/^$oldAttrName: (.*)$/$newAttrName: \1/)
# 2) Objectclasses to rename (s/^objectClass: $oldOC/objectClass: $newOC/)
# 3) Attributes in DNs (s/^dn: (.*,)?$oldAttrName=(.*)$/dn: \1$newAttrName=$2/) (several passes may be necessary!)
# 4) Branch renames - the DN must be changed, and also the value in the entry
#    (ie, when "ou=Configuration Rules" becomes "ou=Rules" we must change the dn: line and the ou: line)
# 5) Deeper renames: some special objects have standard attribute values that need changing (cn, description...)
# Note: there are no DN-type attributes that need changing! Thank you :)

my $currentLine;
my $previousLine;
my $skipLinesUntilNextEntry = 0;

while (<LDIF_FILE>) {
	# Is this line a continuation of the previous line?
	if ( /^ / ) {
		# Remove the line break from the current line buffer,
		# remove the space from the new line, and concat them together
		$currentLine =~ s/\n//;
		s/^ //;
		$currentLine .= $_;
		next; # Continue to the next line
	}
	else {
		# This is a new attribute (or DN) (or an empty line or a comment)

		# Reinitialize our line buffer
		$previousLine = $currentLine;
		$currentLine = $_;

		if ( defined $previousLine ) {
			# Let's handle the last one now, that's in $previousLine

			# Special case: we are in the middle of an entry that we want to replace completely
			if ( ( not $previousLine =~ /^\n$/ ) &&  $skipLinesUntilNextEntry == 1 ) {
				if ( not $previousLine =~ /^(structuralObjectClass|entryUUID|creatorsName|createTimestamp|initTimestamp|entryCSN|objectClass|serial|modifiersName|modifyTimestamp)::? /i ) {
					# Do nothing, just ignore this line
					next;
				}
			}

			if ( $previousLine =~ /^$/ ) {
				# New entry, reset the flag for skipping lines until next entry
				$skipLinesUntilNextEntry = 0;
			}

			# Some branches need renaming (case 4 and 5 above)
			if ( $previousLine =~ /^dn: / ) {
				# This line is a DN - check if we need to change it
				# (more than just attribute renaming which is handled in the next case)

				(my $dn) = $previousLine =~ /^dn: (.*)$/;

				if ( defined $branchDict{lc "$dn"} ) {
					# Change the whole entry:
					# 1) Output the new entry
					# 2) Set a flag to ignore all lines in the input file until the end of the entry
					print RES_FILE $branchDict{lc "$dn-fullentry"};
					$skipLinesUntilNextEntry = 1;
					next;
				}

				# Check to see if this is a sub-entry below a branch that needs renaming
				foreach my $dnToReplace ( keys %branchDict ) {
					$previousLine =~ s/$dnToReplace/$branchDict{lc $dnToReplace}/i;
				}
			}

			# General case: replace attributes and objectClass names (cases 1, 2 and 3 in description above)
			if ( $previousLine =~ /^[a-zA-Z]+::? / ) {
				replaceNames $previousLine;
				next;
			}

			# By default, just copy out this line
			print RES_FILE $previousLine;
		}

	}
}

close RES_FILE;
close LDIF_FILE;

rename ($LDIF_FILENAME . ".tmp", $LDIF_FILENAME);
