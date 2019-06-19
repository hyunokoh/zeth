#ifndef __ZETH_NOTE_HPP__
#define __ZETH_NOTE_HPP__

#include <array>

#include "types/bits.hpp"

namespace libzeth {

class BaseNote {
protected:
    bits64 value_;
public:
    BaseNote() { value_.fill(false); }
    BaseNote(bits64 value) : value_(value) {};
    virtual ~BaseNote() {};

    inline bits64 value() const { return value_; };

    // Test if the note is a 0-valued note
    inline bool is_zero_valued() const {
        bits64 zero;
        zero.fill(false);
        return value_ == zero;
    }
};

class ZethNote : public BaseNote {
public:
    bits256 a_pk; // 256-bit vector
    bits256 rho; // 256-bit vector
    bits384 r; // 384-bit random vector
    //bits256 cm; // 256-bit vector

    ZethNote(bits256 a_pk, bits64 value, bits256 rho, bits384 r/*, bits256 cm*/)
        : BaseNote(value), a_pk(a_pk), rho(rho), r(r) /*, cm(cm)*/{}

    ZethNote(){};
    virtual ~ZethNote() {};
};

class FBaseNote {
protected:
    int value_ =0;
public:
    FBaseNote(){}
    FBaseNote(int value) : value_(value) {};
    virtual ~FBaseNote() {};

    inline int value() const { return value_; };

    // Test if the note is a 0-valued note
    inline bool is_zero_valued() const {
        return value_ == 0;
    }
    
};

class FZethNote : public FBaseNote {
public:
    int a_pk; // 256-bit vector
    int rho; // 256-bit vector
    int r; // 384-bit random vector
    int r_mask;
    //bits256 cm; // 256-bit vector

    FZethNote(int a_pk, int value, int rho, int r, int r_mask/*, bits256 cm*/)
        : FBaseNote(value), a_pk(a_pk), rho(rho), r(r), r_mask(r_mask) /*, cm(cm)*/{}

    FZethNote(){};
    virtual ~FZethNote() {};
};

} // libzeth

#endif // __ZETH_NOTE_HPP__