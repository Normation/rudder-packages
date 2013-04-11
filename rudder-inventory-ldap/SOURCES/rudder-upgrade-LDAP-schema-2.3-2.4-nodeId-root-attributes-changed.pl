#!/usr/bin/perl
## Migration script which does these actions:
##
## 1. Store in a list some attribute names to check.
##
## 2. Read all backuped LDIF until to reach nodeId=root,ou=Nodes,cn=rudder-configuration
##    and put a flag until to reach empty line.
##
## 3. Read and rewrite all backuped LDIF until to reach flag and compare in its buffer
##    with the variables defined in 1 until to reach empty line.
##
##   3.1 If the attribute name doesn't match, rewrite the data in the backuped LDIF.
##
##   3.2 If the attribute name does match, store the data in a variable and don't rewrite the data.
##
## 4. Read all backuped LDIF until to reach
##    nodeId=root,ou=Accepted Inventories,ou=Inventories,cn=rudder-configuration
##    and put a flag until to reach empty line.
##
## 5. Read and rewrite all backup LDIF until to reach flag.
##
## 6. Read and rewrite all backuped LDIF until to reach empty line.
##
##    6.1 If the attribute name does match the data, replace by data stored in 3.2.
##
##    6.2 If the attribute doesn't match the data, rewrite the data in the backuped LDIF.

use strict;
use warnings;
use English qw(-no_match_vars);

my $TARGET_DN = "dn: nodeId=root,ou=Nodes,ou=Accepted Inventories,ou=Inventories,cn=rudder-configuration";

my @TARGET_OBJECTCLASSES = qw(top node unixNode linuxNode);
my %targetAttributes;
$targetAttributes{'nodeId:'} = "root";
$targetAttributes{'osKernelVersion:'} = "1.0-dummy-version";
$targetAttributes{'osName:'} = "Linux";
$targetAttributes{'osVersion:'} = "Linux";
$targetAttributes{'localAccountName:'} = "root";
$targetAttributes{'cn:'} = "root";
$targetAttributes{'localAdministratorAccountName:'} = "root";
$targetAttributes{'nodeHostname:'} = "localhost";
$targetAttributes{'PolicyServerId:'} = "root";
$targetAttributes{'inventoryDate:'} = "19700101000000+0200";
$targetAttributes{'receiveDate:'} = "19700101000000+0200";
$targetAttributes{'ipHostNumber:'} = "127.0.0.1";
$targetAttributes{'agentName:'} = "Community";
$targetAttributes{'publicKey:'} = "Currently not used";


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

# Attribute names to check in the LDIF
my @attributeNames=qw(nodeHostname publicKey ipHostNumber agentName inventoryDate localAdministratorAccountName policyServerId);

# Open temporary output file
open(RES_FILE, ">", $LDIF_FILENAME . ".tmp") or die("Error opening temporary file to write: $!");

# Open input file
open(LDIF_FILE, $LDIF_FILENAME) or die "Can't open LDIF file '$LDIF_FILENAME': $!";

my $currentLine;
my $previousLine;
my $inEntryToClean = 0;
my $inEntryToUpdate = 0;
my %savedAttributeValues;

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

			if ( $previousLine =~ /^$/ ) {
				# Empty line, reset the flag
				$inEntryToClean = 0;
				$inEntryToUpdate = 0;
			}

			if ( $previousLine =~ /^dn: nodeId=root,ou=Nodes,cn=rudder-configuration$/i ) {
				$inEntryToClean = 1;
			}

			if ( $inEntryToClean == 1) {
				# For each attribute names check if the line matches
				my $attributeNameRegexp = join('|', @attributeNames);
				if ($previousLine =~ /^(($attributeNameRegexp)::?) (.*)$/i ) {
					$savedAttributeValues{$1} = $3;
					next; # Don't print this line
				}
			}

			if ( $previousLine =~ /^${TARGET_DN}$/i ) {
				$inEntryToUpdate = 1;
				next;
			}

			if ( $inEntryToUpdate == 1 ) {
				if ( $previousLine =~ /^objectClass::? .*$/i ) {
					next;
				}
				$previousLine =~ /^([^:]+::?) (.*)$/i;
				$targetAttributes{$1} = $2;
				next;
			}

			# By default, just copy out this line
			print RES_FILE $previousLine;
		}

	}
}

# We have checked all the LDIF and got all the values
# They have to be reinserted in the LDIF file

print RES_FILE "\n$TARGET_DN\n";
foreach my $oc (@TARGET_OBJECTCLASSES) {
	print RES_FILE "objectClass: $oc\n";
}
foreach my $savedAttr (keys(%savedAttributeValues)) {
	$targetAttributes{$savedAttr} = $savedAttributeValues{$savedAttr};
}
foreach my $attr (keys(%targetAttributes)) {
	print RES_FILE "$attr $targetAttributes{$attr}\n"; 
}
print RES_FILE "\n";

close RES_FILE;
close LDIF_FILE;

rename ($LDIF_FILENAME . ".tmp", $LDIF_FILENAME);
