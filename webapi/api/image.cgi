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

my $obj_cgi = new PNAPI::CGI;
my $obj_config = new PNAPI::Config;

# XXX: include auth module call here

my $c_target = $obj_cgi->param('target'); # target camera name
# target datetime calculation
#  near: aXXX for after, bXXX for before, XXX in seconds
#  date/time exist, near missing: return exact match, or DEF_NO_TARGET
#  date/time exist, near exist: return exact match, or nearest before/after within time
#  date/time missing: return latest (regardless of near) => date/time = NOW() with near = 'b'
my $c_tgt_date = $obj_cgi->param('date'); # target date, format YYYYMMDD (now if not specified)
my $c_tgt_time = $obj_cgi->param('time'); # target time, format HHMMSS (now if not specified)
my $c_tgt_near = $obj_cgi->param('near'); # if specified, search nearest per specified
my $c_img_width = $obj_cgi->param('w'); # return width
my $c_img_height = $obj_cgi->param('h'); # return height, overrided if width is specified
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

my $obj_tgtroot = $obj_config->get('storage') . '/' . $c_target . '/' . PNAPI::Constants::IMG_DNAME . '/';
my $t_near_flag = undef;
my $t_near_sec = 0;
if (defined($c_tgt_near)) {
  if ($c_tgt_near =~ /^([ab])(\d*)$/) {
    $t_near_flag = $1;
    $t_near_sec = $2 || 0;
  } else {
    $obj_cgi->send_error(DEF_PARAM_ERR, "parameter error (near)");
    exit;
  }
}
my ($t_date, $t_time);
my $t_dt = DateTime->now( time_zone => 'local' );
if ((! defined($c_tgt_date)) && (! defined($c_tgt_time))) {
  $t_near_flag = 'b';
}
if (defined($c_tgt_date)) {
  if ($c_tgt_date !~ /^(\d{4})(\d{2})(\d{2})$/) {
    $obj_cgi->send_error(DEF_PARAM_ERR, "parameter error (date)");
    exit;
  }
  $t_date = $c_tgt_date;
  $t_dt->set(year => $1, month => $2, day => $3);
} else {
  $t_date = $t_dt->ymd('');
}
if (defined($c_tgt_time)) {
  if ($c_tgt_time !~ /^(\d{2})(\d{2})(\d{2})$/) {
    $obj_cgi->send_error(DEF_PARAM_ERR, "parameter error (time)");
    exit;
  }
  $t_time = $c_tgt_time;
  $t_dt->set(hour => $1, minute => $2, second => $3);
} else {
  $t_time = $t_dt->hms('');
}

my $t_fname = undef;
if (! -d $obj_tgtroot) {
  $obj_cgi->send_error(DEF_NO_TARGET, 'target not found (storage)');
  exit;
}
if (-f $obj_tgtroot . '/' . $t_date . '/' . $t_date . $t_time . '.' . $obj_tgt->{'ext'}) {
  $t_fname = $obj_tgtroot . '/' . $t_date . '/' . $t_date . $t_time . '.' . $obj_tgt->{'ext'};
} else {
  if (! defined($t_near_flag)) {
    $obj_cgi->send_error(DEF_NO_TARGET, 'target not found (exact)');
    exit;
  }
  my ($to_dt, $to_date, $to_time);
  $to_dt = $t_dt->clone;
  if ($t_near_flag eq 'a') {
    $to_dt->add(seconds => $t_near_sec);
  } else {
    $to_dt->subtract(seconds => $t_near_sec);
  }
  $to_date = $to_dt->ymd('');
  $to_time = $to_dt->hms('');
  my $t_ext = $obj_tgt->{'ext'};
  if (-d $obj_tgtroot . '/' . $t_date) {
    # 1st: search for the day
    opendir(my $dh, $obj_tgtroot . '/' . $t_date);
    my @files = readdir($dh);
    closedir($dh);
    my $c_ctgt = undef;
    foreach (@files) {
      if ($_ =~ /^\d{8}(\d{6}).$t_ext$/) {
        # just pick the nearest, check condition later
        if ((($t_near_flag eq 'a') && ($1 > $t_time) && ((! defined($c_ctgt)) || ($1 < $c_ctgt))) ||
            (($t_near_flag eq 'b') && ($1 < $t_time) && ((! defined($c_ctgt)) || ($1 > $c_ctgt)))) {
          $c_ctgt = $1;
        }
      }
    }
    if (defined($c_ctgt)) {
      if (($t_near_sec == 0) || ($to_date != $t_date)) {
        $t_fname = $obj_tgtroot . '/' . $t_date . '/' . $t_date . $c_ctgt . '.' . $t_ext;
      } elsif ((($t_near_flag eq 'a') && ($c_ctgt < $to_time)) ||
               (($t_near_flag eq 'b') && ($c_ctgt > $to_time))) {
        $t_fname = $obj_tgtroot . '/' . $t_date . '/' . $t_date . $c_ctgt . '.' . $t_ext;
      } # else could be not found, but treat at first step of 2nd round
    }
  }
  if (! defined($t_fname)) {
    # 2nd: search for the nearest day
    if (($t_near_sec != 0) && ($to_date == $t_date)) {
      $obj_cgi->send_error(DEF_NO_TARGET, 'target not found (range)');
      exit;
    }
    # obj_tgtroot shall exist (already checked)
    opendir(my $dh, $obj_tgtroot);
    my @dirs = readdir($dh);
    closedir($dh);
    my $c_dtgt = undef;
    # search the nearest target date
    # image storage is limited to certain range of days, performance is not issue here
    foreach (@dirs) {
      if ($_ =~ /^\d{8}$/) {
        if ((($t_near_flag eq 'a') && ($_ > $t_date) && ($_ <= $to_date) && ((! defined($c_dtgt)) || ($_ < $c_dtgt))) ||
            (($t_near_flag eq 'b') && ($_ < $t_date) && ($_ >= $to_date) && ((! defined($c_dtgt)) || ($_ > $c_dtgt)))) {
          $c_dtgt = $_;
        }
      }
    }
    if (defined($c_dtgt)) {
      if ($c_dtgt != $t_date) { $t_near_sec = 0; } # if date is not at edge, pick any at most side
      my $c_ttgt = undef;
      opendir(my $dh, $obj_tgtroot . '/' . $c_dtgt);
      my @files = readdir($dh);
      closedir($dh);
      foreach (@files) {
        if ($_ =~ /^\d{8}(\d{6}).$t_ext$/) {
          # search most (only)
          if ((($t_near_flag eq 'a') && ((! defined($c_ttgt)) || ($1 < $c_ttgt))) ||
              (($t_near_flag eq 'b') && ((! defined($c_ttgt)) || ($1 > $c_ttgt)))) {
            $c_ttgt = $1;
          }
        }
      }
      if (defined($c_ttgt)) {
        if ((($t_near_flag eq 'a') && (($c_dtgt != $t_date) || ($c_ttgt <= $to_time))) ||
            (($t_near_flag eq 'b') && (($c_dtgt != $t_date) || ($c_ttgt >= $to_time)))) {
          $t_fname = $obj_tgtroot . '/' . $c_dtgt . '/' . $c_dtgt . $c_ttgt . '.' . $t_ext;
        }
      }
    }
  }
}
if (! defined($t_fname)) {
  $obj_cgi->send_error(DEF_NO_TARGET, 'target not found (range)');
  exit;
}

# start conversion from found source image to ordered size
if (! (defined($c_img_height) || defined($c_img_width))) {
  $obj_cgi->set_type(PNAPI::Constants::IMG_FMT->{$obj_tgt->{'ext'}});
  print $obj_cgi->header(200,
    -Content_Disposition => 'inline; filename="' . (split('/', $t_fname))[-1] . '"',
  );
  binmode STDOUT, ':bytes';
  open(INDAT, $t_fname);
  print <INDAT>;
  close(INDAT);
  exit;
}

load('Image::Magick');
my $c_imk = Image::Magick->new;
$c_imk->Read($t_fname);
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
  -Content_Disposition => 'inline; filename="' . (split('/', $t_fname))[-1] . $c_fadd . '"',
);
binmode STDOUT, ':bytes';
$c_imk->Write(PNAPI::Constants::IMG_FMT_DEF_IMK);

exit;