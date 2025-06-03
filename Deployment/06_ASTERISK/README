Opus Software Codec for Asterisk README

==[ Installation Overview ]===================================================

  There are two ways to install codec_opus on your system

  The preferred way of installing the Opus codec is to use menuselect in
  Asterisk to automatically download and install the codec. From the Asterisk
  top-level source directory, run

  1) run `make menuselect`
  2) Highlight "Codec Translators" and press enter.
  3) Scroll down to "codec_opus" in the section labeled "External"
  4) Press enter to select the codec if it is not already selected.
  5) Press "x" to exit menuselect and save your selections.

  From here, build and install Asterisk as you normally would. When you run
  the `make install` step, codec_opus will automatically be downloaded and
  installed into the Asterisk module directory (by default,
  /usr/lib/asterisk/modules/).


  The alternative way to install codec_opus is to download a tarball
  directly from digium.com. Once the tarball is downloaded and untarred,
  perform the following steps:

  1) Copy the codec_opus.so file into the Asterisk module directory (by default,
     /usr/lib/asterisk/modules/).
  2) Copy the codec_opus_config-en_US.xml file into the Asterisk external
     documentation directory (by default,
     /var/lib/asterisk/documentation/thirdparty).

  The codec selecter should ensure that you download the correct version of
  the codec for your version of Asterisk.


==[ Asterisk Configuration ]===================================================

  Asterisk can be given custom configuration instructions for the Opus codec
  using the codecs.conf file. By placing "type = opus" in a configuration
  section, that section will be recognized as having options relating to Opus.

  For a listing of Opus-related options, see the Asterisk wiki's listing of
  codecs.conf options.

==[ Usage Tracking ]===========================================================

  The codec_opus module will periodically attempt to send usage statistics to
  an Asterisk community server. The statistics are sent at most every 24 hours.
  If the module fails to send usage statistics, it will NOT affect the
  operation of the Opus codec.

  copy to us

  The data sent in the statistics are as follows:
    - A randomly generated unique ID for the server running Asterisk.
    - A timestamp showing when the statistics were sent.
    - The highest number of simultaneous Opus encoders/decoders in use
      during the reporting period.
