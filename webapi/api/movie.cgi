#! /usr/bin/perl

use strict;
use lib '../';

use JSON;
use DateTime;
use Module::Load qw( load );

use PNAPI::Constants;
use PNAPI::Config;
use PNAPI::CGI;

use constant DEF_PARAM_ERR  => 503;
use constant DEF_NO_TARGET  => 404;

use constant DEF_P_MODE_THUMB => 'thumb';
use constant MAX_READ => 65536;

my $obj_cgi = new PNAPI::CGI;
my $obj_config = new PNAPI::Config;

my $ret = {};

# XXX: include auth module call here

my $c_target = $obj_cgi->param('target'); # target camera name
my $c_tgt_date = $obj_cgi->param('date'); # target date, format YYYYMMDD (latest if not specified; only exact match)
my $c_tgt_mode = $obj_cgi->param('mode'); # target mode, 'thumb' or undef for anything else
my $c_img_width = $obj_cgi->param('w'); # return width (for thumb mode)
my $c_img_height = $obj_cgi->param('h'); # return height, overrided if width is specified (for thumb mode)
# for movie, HTTP_RANGE will be handled later
my $obj_tgt;

if (defined($c_target)) {
  if (exists $obj_config->get('targets')->{$c_target}) {
    $obj_tgt = $obj_config->get('targets')->{$c_target};
  } else {
    $obj_cgi->send_error(DEF_NO_TARGET, 'target not found');
    exit;
  }
} else {
  $obj_cgi->send_error(DEF_PARAM_ERR, "parameter error (target)");
  exit;
}
my $fdat_name = $obj_config->get('storage') . '/' . $c_target . '/' . PNAPI::Constants::MOV_DNAME . '/';
if (! -d $fdat_name) {
  $obj_cgi->send_error(DEF_NO_TARGET, 'target not found (storage)');
  exit;
}
my $fdat_ext;
my $fdat_fn = undef;
if (defined($c_tgt_mode) && ($c_tgt_mode eq DEF_P_MODE_THUMB)) { $fdat_ext = $obj_tgt->{'ext'}; }
else { $fdat_ext = PNAPI::Constants::MOV_EXT; }
if (defined($c_tgt_date)) {
  $fdat_fn = $c_tgt_date . $fdat_ext;
  $fdat_name .= $fdat_fn;
  if (! -f $fdat_name) {
    $obj_cgi->send_error(DEF_NO_TARGET, 'target not found (file)');
    exit;
  }
} else {
  opendir(my $dh, $fdat_name);
  my @files = readdir($dh);
  closedir($dh);
  foreach (@files) {
    if ($_ =~ /^(\d{8})$fdat_ext$/) { if ((! defined($fdat_fn)) || ($1 > $fdat_fn)) { $fdat_fn = $1; } }
  }
  if (! defined($fdat_fn)) {
    $obj_cgi->send_error(DEF_NO_TARGET, 'target not found (file)');
    exit;
  }
  $fdat_fn .= $fdat_ext;
  $fdat_name .= $fdat_fn;
}

# for thumb mode
if (defined($c_tgt_mode) && ($c_tgt_mode eq DEF_P_MODE_THUMB)) {
  if (! (defined($c_img_height) || defined($c_img_width))) {
    $obj_cgi->set_type(PNAPI::Constants::IMG_FMT->{$obj_tgt->{'ext'}});
    print $obj_cgi->header(200,
      -Content_Disposition => 'inline; filename="' . $fdat_fn . '"',
    );
    binmode STDOUT, ':bytes';
    open(INDAT, $fdat_name);
    print <INDAT>;
    close(INDAT);
  } else {
    load('Image::Magick');
    my $c_imk = Image::Magick->new;
    $c_imk->Read($fdat_name);
    my $c_fadd = '';
    my $c_imk_geo = '';
    if (defined($c_img_width)) {
      $c_imk_geo = $c_img_width . 'x';
      $c_fadd = 'w' . $c_img_width;
    } else {
      $c_imk_geo = 'x' . $c_img_height;
      $c_fadd = 'h' . $c_img_height;
    }
    $c_imk->Thumbnail(geometry => $c_imk_geo);
    $c_fadd = '-' . $c_fadd . '.' . PNAPI::Constants::IMG_FMT_DEF;
    $obj_cgi->set_type(PNAPI::Constants::IMG_FMT->{PNAPI::Constants::IMG_FMT_DEF});
    print $obj_cgi->header(200,
      -Content_Disposition => 'inline; filename="' . $fdat_fn . $c_fadd . '"',
    );
    binmode STDOUT, ':bytes';
    $c_imk->Write(PNAPI::Constants::IMG_FMT_DEF_IMK);
  }
  exit;
}

my $fdat_size = -s $fdat_name;
$obj_cgi->set_type(PNAPI::Constants::MOV_MIME . "; name=\"$fdat_fn\"");
# for movie, check REQUEST_METHOD
if (defined($ENV{'REQUEST_METHOD'}) && ($ENV{'REQUEST_METHOD'} eq 'HEAD')) {
  print $obj_cgi->header(200,
    -content_length => $fdat_size,
    -accept_ranges => 'bytes',
  );
  exit;
}

my $q_range = $ENV{'HTTP_RANGE'};
if (! defined($q_range)) {
  # simply stream
  print $obj_cgi->header(200,
    -content_length => $fdat_size,
    -accept_ranges => 'bytes',
  );
  binmode STDOUT, ':bytes';
  open(INDAT, $fdat_name);
  print <INDAT>;
  close(INDAT);
  exit;
}

my ($qr_start, $qr_end);
if ($q_range !~ /^bytes=([0-9]+)-([0-9]+)$/) {
  $obj_cgi->send_error(DEF_PARAM_ERR, "HTTP_RANGE (invalid format)");
  exit;
}
$qr_start = $1;
$qr_end = $2;
if (($qr_start > $qr_end) || ($qr_end >= $fdat_size)) {
  $obj_cgi->send_error(DEF_PARAM_ERR, "HTTP_RANGE (invalid range)");
  exit;
}

print $obj_cgi->header(200,
  -content_length => ($qr_end - $qr_start + 1),
  -content_range => "bytes $qr_start-$qr_end/" . $fdat_size,
  -accept_ranges => 'bytes',
);
binmode STDOUT, ':bytes';
open(INDAT, $fdat_name);
seek(INDAT, 0, $qr_start);
my $cpos = $qr_start;
my $cbuf;
while (($cpos + MAX_READ) < $qr_end) {
  read INDAT, $cbuf, MAX_READ;
  print $cbuf;
  $cpos += MAX_READ;
}
read INDAT, $cbuf, ($qr_end - $cpos + 1);
print $cbuf;
close(INDAT);
