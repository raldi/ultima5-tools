#! /usr/bin/env python

# Ultima V dialogue bugfixer
# Written by Mike Schiraldi in 2023
# To use, run this in the directory with all the *.TLK files
# Details on the bugs: https://tcrf.net/Ultima_V_(DOS)

import hashlib
import shutil
import sys

fixes = (

# Weblock, when asked about Gorn or Hassad, is supposed to say,
# "He is a prisoner in the dungeon!". However, his dialogue config is broken,
# and instead, when asked about Gorn he says, "hass", and when asked about
# Hassad, says, "I cannot help thee with that".
('CASTLE.TLK', 0x1b2f,
 ( 0xE7, 0xEF, 0xF2, 0xEE, 0x00, 0xE8, 0xE1, 0xF3, 0xF3, 0x00, 0x87, 0x00 ),
 ( 0xE7, 0xEF, 0xF2, 0xEE, 0x00, 0x87, 0x00, 0xE8, 0xE1, 0xF3, 0xF3, 0x00 ),
),

# Malik offers to sell a hint for 3 but then charges 4.
('TOWNE.TLK', 0x06fd, (0xB4,), (0xB3,)),

# Sir Arbuthnot the royal coinmaker can't be asked about his coin, because
# "coin" and "coinmaker" give the same answer.
('DWELLING.TLK', 0x1D6C,
 (0xF2, 0xEF, 0xF9, 0xE1, 0x00, 0x87, 0x00, 0xE3, 0xEF, 0xE9, 0xEE),
 (0xF2, 0xEF, 0xF9, 0x00, 0x87, 0x00, 0xE3, 0xEF, 0xE9, 0xEE, 0xED)),

# Sir Arbuthnot also fails to process an answer to his question about whether
# you're really the Avatar. Fixing this requires extra bytes, but by a
# fortunate coincidence, this is at the end of the file and so we can do that
# without having to reindex anything.
('DWELLING.TLK', 0x1f0d,
 (            0xA7, 0xD4, 0xE9, 0xF3, 0xA0, 0xE9, 0xEE, 0xE4, 0xE5, 0xE5, 0xE4,
  0x37, 0xE8, 0xEF, 0xEE, 0xEF, 0xF2, 0xA1, 0xA2, 0x8D, 0x8D, 0x88, 0xA2, 0x8D,
  0x8D, 0xFF, 0x00, 0x90, 0x9F, 0xC0),
 (0xF9, 0x00, 0xA7, 0xD4, 0xE9, 0xF3, 0xA0, 0xE9, 0xEE, 0xE4, 0xE5, 0xE5, 0xE4,
  0x37, 0xE8, 0xEF, 0xEE, 0xEF, 0xF2, 0xA1, 0xA2, 0x8D, 0x8D, 0x88, 0xA2, 0x8D, 
  0x8D, 0xFF, 0x00, 0x90, 0x9F, 0xC0)),

# Sin'Vraal claims the Shard of Hatred is in the underworld at [ I'A", I'A" ],
# but those coords are actually the entrance to the dungeon Doom; the Shard
# of Hatred is at [ E'B", I'C" ]. Credit to /u/fgw3reddit for pointing this out.
('DWELLING.TLK', 0x15a3,
  (0xC9, 0x8E, 0xA7, 0x8E, 0xC1, 0x8E, 0xA2, 0xAC, 0xA0, 0x8E, 0xC9, 0x8E, 0xA7, 0x8E, 0xC1),
  (0xC5, 0x8E, 0xA7, 0x8E, 0xC2, 0x8E, 0xA2, 0xAC, 0xA0, 0x8E, 0xC9, 0x8E, 0xA7, 0x8E, 0xC3)),

# Mario in Yew has some of his text cut off if you ask about his minor crime.
('TOWNE.TLK', 0x3634, (0x00, 0xA2, 0x8D, 0x8D, 0x83),
                      (0xA2, 0x8D, 0xA0, 0x8D, 0x8F,)),

# Thrud is supposed to give you a Jeweled Sword and Jeweled Shield, but someone
# accidentally typed 28 when they meant to type 0x28 so you get a mundane
# crossbow instead.
('KEEP.TLK', 0x12a9, (28,), (0x28,))
)

sums = {
  'CASTLE.TLK':   'fde54ae7c8852cf52eae3312615997d3',
  'DWELLING.TLK': '28c5669eccccea184c66a488c854fbd5',
  'KEEP.TLK':     'e4fa8962d36a88c81d8cc09dcce82a46',
  'TOWNE.TLK':    '325f55a2f0b533ca53851296d538a1a6'
}

for filename, expected_sum in sums.items():
  try:
    fd = open(filename, 'rb')
  except FileNotFoundError:
    print(f"{filename} not found. Run this from your Ultima V directory.", file=sys.stderr)
    sys.exit(1)
  data = fd.read()
  fd.close()
  summer = hashlib.md5()
  summer.update(data)
  actual_sum = summer.hexdigest()
  if actual_sum != expected_sum:
    print(f"{filename} doesn't look like an original; won't back up or modify")
  else:
    print(f"Backing up {filename} to orig-{filename}")
    shutil.copy(filename, "orig-" + filename)
 
    changed = False
    for i, (fix_filename, offset, expected, replacements) in enumerate(fixes):
      if fix_filename != filename:
        continue
      if data[offset:offset + len(replacements)] == bytes(replacements):
        print(f"{filename} already received patch {i}")
      elif data[offset:offset + len(expected)] != bytes(expected):
        print(f"{filename} doesn't contain expected contents; won't apply patch {i}")
      else:
        data = (data[:offset] + bytes(replacements) + data[offset + len(expected):])
        changed = True 
    if changed:
      fd = open(filename, 'wb')
      fd.write(data)
      fd.close()
      print(f"Wrote new {filename}")
