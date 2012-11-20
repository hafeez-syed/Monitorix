#!/usr/bin/env perl
#
# Monitorix - A lightweight system monitoring tool.
#
# Copyright (C) 2005-2012 by Jordi Sanfeliu <jordi@fibranet.cat>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

no strict;
no warnings;
use FindBin qw($Bin);
use lib $Bin . '/lib';

use Monitorix;
use CGI qw(:standard);
use Config::General;
use POSIX;
use RRDs;

my %config;
my %cgi;
my %colors;
my %tf;
my @version12;
my @version12_small;

#our @nfsv2 = ("null", "getattr", "setattr", "root", "lookup", "readlink", "read", "wrcache", "write", "create", "remove", "rename", "link", "symlink", "mkdir", "rmdir", "readdir", "fsstat");
#our @nfsv3 = ("null", "getattr", "setattr", "lookup", "access", "readlink", "read", "write", "create", "mkdir", "symlink", "mknod", "remove", "rmdir", "rename", "link", "readdir", "readdirplus", "fsstat", "fsinfo", "pathconf", "commit");
#our @nfssv4 = ("op0-unused", "op1-unused", "op2-future", "access", "close", "commit", "create", "delegpurge", "delegreturn", "getattr", "getfh", "link", "lock", "lockt", "locku", "lookup", "lookup_root", "nverify", "open", "openattr", "open_conf", "open_dgrd", "putfh", "putpubfh", "putrootfh", "read", "readdir", "readlink", "remove", "rename", "renew", "restorefh", "savefh", "secinfo", "setattr", "setcltid", "setcltidconf", "verify", "write", "rellockowner", "bc_ctl", "bind_conn", "exchange_id", "create_ses", "destroy_ses", "free_stateid", "getdirdeleg", "getdevinfo", "getdevlist", "layoutcommit", "layoutget", "layoutreturn", "secinfononam", "sequence", "set_ssv", "test_stateid", "want_deleg", "destroy_clid", "reclaim_comp");
#our @nfscv4 = ("null", "read", "write", "commit", "open", "open_conf", "open_noat", "open_dgrd", "close", "setattr", "fsinfo", "renew", "setclntid", "confirm", "lock", "lockt", "locku", "access", "getattr", "lookup", "lookup_root", "remove", "rename", "link", "symlink", "create", "pathconf", "statfs", "readlink", "readdir", "server_caps", "delegreturn", "getacl", "setacl", "fs_locations", "exchange_id", "create_ses", "destroy_ses", "sequence", "get_lease_t", "reclaim_comp", "layoutget", "layoutcommit", "layoutreturn", "getdevlist", "getdevinfo", "ds_write", "ds_commit");

sub graph_header {
	my ($title, $colspan) = @_;
	print("\n");
	print("  <table cellspacing='5' cellpadding='0' width='1' bgcolor='$colors{graph_bg_color}' border='1'>\n");
	print("    <tr>\n");
	print("      <td bgcolor='$colors{title_bg_color}' colspan='$colspan'>\n");
	print("        <font face='Verdana, sans-serif' color='$colors{title_fg_color}'>\n");
	print("          <b>&nbsp;&nbsp;$title<b>\n");
	print("        </font>\n");
	print("      </td>\n");
	print("    </tr>\n");
}

sub graph_footer {
	print("  </table>\n");
}


# MAIN
# ----------------------------------------------------------------------------
open(IN, "< monitorix.conf.path");
my $config_path = <IN>;
chomp($config_path);
close(IN);

if(! -f $config_path) {
	print(<< "EOF");
Content-Type: text/plain

FATAL: Monitorix is unable to continue!
=======================================

File 'monitorix.conf.path' not found.

Please make sure that 'base_dir' option is correctly configured and that
this CGI is located in the 'base_dir'/cgi-bin/ directory.

And don't forget to restart Monitorix for the changes to take effect.
EOF
	die "FATAL: File 'monitorix.conf.path' not found!";
}

my $conf = new Config::General(
	-ConfigFile => $config_path,
);
%config = $conf->getall;

$config{url} = $ENV{HTTPS} ? "https://" . $ENV{HTTP_HOST} : "http://" . $ENV{HTTP_HOST};
$config{hostname} = $ENV{SERVER_NAME};
if(!($config{hostname})) {	# called from the command line
	$config{hostname} = "127.0.0.1";
	$config{url} = "http://127.0.0.1";
}
$config{url} .= $config{base_url} . "/";

# get the current OS and kernel version
my $release;
($config{os}, undef, $release) = uname();
my ($major, $minor) = split('\.', $release);
$config{kernel} = $major . "." . $minor;

my $mode = defined(param('mode')) ? param('mode') : '';
my $graph = param('graph');
my $when = param('when');
my $color = param('color');
my $val = defined(param('val')) ? param('val') : '';
my $silent = defined(param('silent')) ? param('silent') : '';
if($mode ne "localhost") {
	($mode, $val)  = split(/\./, $mode);
}

print("Content-Type: text/html\n");
print("\n");

# default white theme colors
$colors{graph_colors} = ();
$colors{warning_color} = "--color=CANVAS#880000";
$colors{bg_color} = "#FFFFFF";
$colors{fg_color} = "#000000";
$colors{title_bg_color} = "#777777";
$colors{title_fg_color} = "#CCCC00";
$colors{graph_bg_color} = "#CCCCCC";

if($color) {
	if($color eq "black") {
		push(@{$colors{graph_colors}}, "--color=CANVAS#" . $config{$color}->{canvas});
		push(@{$colors{graph_colors}}, "--color=BACK#" . $config{$color}->{back});
		push(@{$colors{graph_colors}}, "--color=FONT#" . $config{$color}->{font});
		push(@{$colors{graph_colors}}, "--color=MGRID#" . $config{$color}->{mgrid});
		push(@{$colors{graph_colors}}, "--color=GRID#" . $config{$color}->{grid});
		push(@{$colors{graph_colors}}, "--color=FRAME#" . $config{$color}->{frame});
		push(@{$colors{graph_colors}}, "--color=ARROW#" . $config{$color}->{arrow});
		push(@{$colors{graph_colors}}, "--color=SHADEA#" . $config{$color}->{shadea});
		push(@{$colors{graph_colors}}, "--color=SHADEB#" . $config{$color}->{shadeb});
		push(@{$colors{graph_colors}}, "--color=AXIS#" . $config{$color}->{axis}) if defined($config{$color}->{axis});
		$colors{bg_color} = $config{$color}->{main_bg};
		$colors{fg_color} = $config{$color}->{main_fg};
		$colors{title_bg_color} = $config{$color}->{title_bg};
		$colors{title_fg_color} = $config{$color}->{title_fg};
		$colors{graph_bg_color} = $config{$color}->{graph_bg};
	}
}

($tf{twhen}) = ($when =~ m/(hour|day|week|month|year)$/);
($tf{nwhen} = $when) =~ s/$tf{twhen}// unless !$tf{twhen};
$tf{nwhen} = 1 unless $tf{nwhen};
$tf{twhen} = "day" unless $tf{twhen};
$tf{when} = $tf{nwhen} . $tf{twhen};

# toggle this to 1 if you want to maintain old (2.3-) Monitorix with Multihost
if($backwards_compat_old_multihost) {
	$tf{when} = $tf{twhen};
}

our ($res, $tc, $tb, $ts);
if($tf{twhen} eq "day") {
	($tf{res}, $tf{tc}, $tf{tb}, $tf{ts}) = (3600, 'h', 24, 1);
}
if($tf{twhen} eq "week") {
	($tf{res}, $tf{tc}, $tf{tb}, $tf{ts}) = (108000, 'd', 7, 1);
}
if($tf{twhen} eq "month") {
	($tf{res}, $tf{tc}, $tf{tb}, $tf{ts}) = (216000, 'd', 30, 1);
}
if($tf{twhen} eq "year") {
	($tf{res}, $tf{tc}, $tf{tb}, $tf{ts}) = (5184000, 'd', 365, 1);
}


if($RRDs::VERSION > 1.2) {
	push(@version12, "--slope-mode");
	push(@version12, "--font=LEGEND:7:");
	push(@version12, "--font=TITLE:9:");
	push(@version12, "--font=UNIT:8:");
	if($RRDs::VERSION >= 1.3) {
		push(@version12, "--font=DEFAULT:0:Mono");
	}
	if($tf{twhen} eq "day") {
		push(@version12, "--x-grid=HOUR:1:HOUR:6:HOUR:6:0:%R");
	}
	push(@version12_small, "--font=TITLE:8:");
	push(@version12_small, "--font=UNIT:7:");
	if($RRDs::VERSION >= 1.3) {
		push(@version12_small, "--font=DEFAULT:0:Mono");
	}
}


if(!$silent) {
	my $title;
	my $str;

	print("<html>\n");
	print("  <head>\n");
	print("    <title>$config{title}</title>\n");
	print("    <link rel='shortcut icon' href='" . $config{base_url} . "/" . $config{favicon} . "'>\n");
	if($config{refresh_rate}) {
		print("    <meta http-equiv='Refresh' content='" . $config{refresh_rate} . "'>\n");
	}
	print("  </head>\n");
	print("  <body bgcolor='" . $colors{bg_color} . "' vlink='#888888' link='#888888'>\n");
	print("  <center>\n");
	print("  <table cellspacing='5' cellpadding='0' bgcolor='" . $colors{graph_bg_color} . "' border='1'>\n");
	print("  <tr>\n");
	if(($val ne "all" || $val ne "group") && $mode ne "multihost") {
		print("  <td bgcolor='" . $colors{title_bg_color} . "'>\n");
		print("  <font face='Verdana, sans-serif' color='" . $colors{title_fg_color} . "'>\n");
		print("    <font size='5'><b>&nbsp;&nbsp;Host:&nbsp;<b></font>\n");
		print("  </font>\n");
		print("  </td>\n");
	}
	if($val =~ m/group[0-9]+/) {
		my $gnum = substr($val, 5, length($val));
		my $gname = (split(',', $config{remotegroup_list}))[$gnun];
		$gname = trim($gname);
		print("  <td bgcolor='" . $colors{title_bg_color} . "'>\n");
		print("  <font face='Verdana, sans-serif' color='" . $colors{title_fg_color} . "'>\n");
		print("    <font size='5'><b>&nbsp;&nbsp;$gname&nbsp;<b></font>\n");
		print("  </font>\n");
		print("  </td>\n");
	}
	print("  <td bgcolor='" . $colors{bg_color} . "'>\n");
	print("  <font face='Verdana, sans-serif' color='" . $colors{fg_color} . "'>\n");
	if($mode eq "localhost" || $mode eq "pc") {
		$title = $config{hostname};
	} elsif($mode eq "multihost") {
		$graph = $graph eq "all" ? "_system1" : $graph;
		if(substr($graph, 0, 4) eq "_net") {
			$str = "_net" . substr($graph, 5, 1);
			$title = $config{graphs}->{$str};
		} elsif(substr($graph, 0, 5) eq "_port") {
			$str = substr($graph, 0, 5);
			my $p = substr($graph, 5, 1);
			$title = $config{graphs}->{$str};
			$p = (split(',', $config{port_list}))[$p];
			$title .= " " . trim($p);
			$p = (split(',', $config{port_desc}->{$p}))[0];
			$title .= " (" . trim($p) . ")";
		} else {
			$title = $config{graphs}->{$graph};
		}
	}
	$title =~ s/ /&nbsp;/g;
	print("    <font size='5'><b>&nbsp;&nbsp;$title&nbsp;&nbsp;</b></font>\n");
	print("  </font>\n");
	print("  </td>\n");
		print("  <td bgcolor='" . $colors{title_bg_color} . "'>\n");
		print("  <font face='Verdana, sans-serif' color='" . $colors{title_fg_color} . "'>\n");
		print("    <font size='5'><b>&nbsp;&nbsp;last&nbsp;$tf{twhen}&nbsp;&nbsp;<b></font>\n");
		print("  </font>\n");
		print("  </td>\n");
	print("  </tr>\n");
	print("  </table>\n");
	print("  <font face='Verdana, sans-serif' color='" . $colors{fg_color} . "'>\n");
	print("    <h4><font color='#888888'>" . strftime("%a %b %e %H:%M:%S %Z %Y", localtime) . "</font></h4>\n");
}


$cgi{colors} = \%colors;
$cgi{tf} = \%tf;
$cgi{version12} = \@version12;
$cgi{version12_small} = \@version12_small;
$cgi{graph} = $graph;
$cgi{silent} = $silent;

if($mode eq "localhost") {
	foreach (split(',', $config{graph_name})) {
		my $g = trim($_);
		if(lc($config{graph_enable}->{$g}) eq "y") {
			my $cgi = $g . "_cgi";

			eval "use $g qw(" . $cgi . ")";
			if($@) {
				print(STDERR "WARNING: unable to find module '$g'\n");
				next;
			}

			if($graph eq "all" || $graph =~ /_$g/) {
				no strict "refs";
				&$cgi($g, \%config, \%cgi);
			}
		}
	}
} elsif($mode eq "multihost") {
	multihost();
} elsif($mode eq "pc") {
	pc();
}

if(!$silent) {
	print("\n");
	print("  </font>\n");
	print("  </center>\n");
	print("  <p>\n");
	print("  <a href='http://www.monitorix.org'><img src='" . $config{url} . "logo_bot.png' border='0'></a>\n");
	print("  <br>\n");
	print("  <font face='Verdana, sans-serif' color='" . $colors{fg_color} . "' size='-2'>\n");
	print("Copyright &copy; 2005-2012 Jordi Sanfeliu\n");
	print("  </font>\n");
	print("  </body>\n");
	print("</html>\n");
}

0;